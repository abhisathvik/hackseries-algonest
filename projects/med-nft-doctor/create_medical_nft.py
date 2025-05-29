import os
import requests
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.future.transaction import AssetConfigTxn

# ---------- CONFIGURATION ----------
ALGOD_TOKEN = "YOUR_ALGOD_API_KEY"
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
WEB3_STORAGE_TOKEN = "YOUR_WEB3_STORAGE_API_TOKEN"
INPUT_FILE = "prescription.pdf"  # your original prescription
PATIENT_ADDRESS = "PATIENT_WALLET_ADDRESS"  # for metadata reference

# ---------- 1. ENCRYPT FILE ----------
def encrypt_file(input_file_path, output_file_path, key):
    cipher = AES.new(key, AES.MODE_EAX)
    with open(input_file_path, 'rb') as f:
        plaintext = f.read()
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    with open(output_file_path, 'wb') as f:
        f.write(cipher.nonce + tag + ciphertext)
    return key.hex()

# ---------- 2. UPLOAD TO IPFS ----------
def upload_to_ipfs(file_path, api_token):
    headers = {"Authorization": f"Bearer {api_token}"}
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        response = requests.post("https://api.web3.storage/upload", headers=headers, files=files)
    cid = response.json()['cid']
    return cid

# ---------- 3. MINT NFT ----------
def mint_nft(creator_mnemonic, ipfs_cid, patient_address):
    algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
    creator_private_key = mnemonic.to_private_key(creator_mnemonic)
    creator_address = account.address_from_private_key(creator_private_key)

    params = algod_client.suggested_params()
    asset_url = f"ipfs://{ipfs_cid}"

    txn = AssetConfigTxn(
        sender=creator_address,
        sp=params,
        total=1,
        decimals=0,
        default_frozen=False,
        unit_name="MEDNFT",
        asset_name="Encrypted Prescription",
        manager=creator_address,
        reserve=creator_address,
        freeze=None,
        clawback=None,
        url=asset_url,
        note=f"Patient: {patient_address}".encode(),
        strict_empty_address_check=False
    )

    stxn = txn.sign(creator_private_key)
    txid = algod_client.send_transaction(stxn)
    print("NFT Minted. Transaction ID:", txid)

# ---------- MAIN FLOW ----------
def main():
    encrypted_file = INPUT_FILE + ".enc"
    encryption_key = get_random_bytes(32)  # AES-256

    print("[+] Encrypting file...")
    key_hex = encrypt_file(INPUT_FILE, encrypted_file, encryption_key)
    print("    Encryption key (hex):", key_hex)

    print("[+] Uploading to IPFS...")
    cid = upload_to_ipfs(encrypted_file, WEB3_STORAGE_TOKEN)
    print("    IPFS CID:", cid)

    print("[+] Minting NFT on Algorand...")
    creator_mnemonic = input("Enter Doctor's wallet mnemonic: ")
    mint_nft(creator_mnemonic, cid, PATIENT_ADDRESS)

    print("\n✅ Done! Store the encryption key securely.")

if __name__ == "__main__":
    main()
