from pyteal import *

def approval_program():
    # Global keys
    creator = Bytes("creator")      # Doctor's wallet
    owner = Bytes("owner")          # Patient's wallet
    ipfs_cid = Bytes("cid")         # Encrypted CID
    access = Bytes("access")        # Who can view
    revoked = Bytes("revoked")      # Access revoked flag

    # App creation (mint NFT)
    on_create = Seq([
        Assert(Txn.application_args.length() == Int(2)),  # [cid, owner]
        App.globalPut(creator, Txn.sender()),
        App.globalPut(ipfs_cid, Txn.application_args[0]),  # Encrypted IPFS CID
        App.globalPut(owner, Txn.application_args[1]),
        App.globalPut(revoked, Int(0)),
        App.globalPut(access, Global.zero_address()),  # No one has access initially
        Return(Int(1))
    ])

    # Share NFT (only patient can share)
    share_access = Seq([
        Assert(Txn.application_args.length() == Int(2)),  # ["share", address]
        Assert(Txn.sender() == App.globalGet(owner)),
        App.globalPut(access, Txn.application_args[1]),
        App.globalPut(revoked, Int(0)),
        Return(Int(1))
    ])

    # Revoke access (only patient)
    revoke_access = Seq([
        Assert(Txn.sender() == App.globalGet(owner)),
        App.globalPut(revoked, Int(1)),
        Return(Int(1))
    ])

    # View CID (only if not revoked)
    view_access = Seq([
        Assert(App.globalGet(revoked) == Int(0)),
        Assert(Txn.sender() == App.globalGet(access)),
        Return(Int(1))
    ])

    # Handle NoOp calls (custom methods)
    handle_noop = Cond(
        [Txn.application_args[0] == Bytes("share"), share_access],
        [Txn.application_args[0] == Bytes("revoke"), revoke_access],
        [Txn.application_args[0] == Bytes("view"), view_access],
    )

    # Program routing
    program = Cond(
        [Txn.application_id() == Int(0), on_create],
        [Txn.on_completion() == OnComplete.NoOp, handle_noop],
    )

    return program

def clear_state_program():
    return Return(Int(1))
