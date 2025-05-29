from pyteal import *

def approval():
    owner = Bytes("owner")       # Global: patient address
    viewer = Bytes("viewer")     # Global: who can view
    expires = Bytes("expires")   # Global: time limit

    on_create = Seq([
        App.globalPut(owner, Txn.sender()),
        App.globalPut(viewer, Global.zero_address()),
        App.globalPut(expires, Int(0)),
        Approve()
    ])

    is_owner = Txn.sender() == App.globalGet(owner)

    # Set viewer and expiry
    set_viewer = Seq([
        Assert(is_owner),
        App.globalPut(viewer, Txn.application_args[1]),
        App.globalPut(expires, Btoi(Txn.application_args[2])),  # timestamp
        Approve()
    ])

    # Revoke viewer
    revoke_viewer = Seq([
        Assert(is_owner),
        App.globalPut(viewer, Global.zero_address()),
        App.globalPut(expires, Int(0)),
        Approve()
    ])

    # Check if viewer is allowed
    view_allowed = And(
        Txn.sender() == App.globalGet(viewer),
        Global.latest_timestamp() <= App.globalGet(expires)
    )

    allow_view = If(view_allowed, Approve(), Reject())

    program = Cond(
        [Txn.application_id() == Int(0), on_create],
        [Txn.on_completion() == OnComplete.NoOp, Cond(
            [Txn.application_args[0] == Bytes("set_viewer"), set_viewer],
            [Txn.application_args[0] == Bytes("revoke_viewer"), revoke_viewer],
            [Txn.application_args[0] == Bytes("view"), allow_view]
        )],
    )

    return program

def clear():
    return Approve()
