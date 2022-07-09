pragma solidity ^0.8.0;
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
contract FakeNFT is Ownable, ERC721("FakeNFT", "FNFT"){
bytes32 private EIP712_DOMAIN_TYPE_HASH = keccak256("EIP712Domain(string name,string version)");
bytes32 private DOMAIN_SEPARATOR = keccak256(abi.encode(EIP712_DOMAIN_TYPE_HASH, keccak256(bytes("Quixotic")), keccak256(bytes("4"))));
    function MintNFT(address to, uint tokenID) external onlyOwner{
        _mint(to, tokenID);
    }

    function generateSellerDigest(
    address payable seller, 
    address contractAddress, 
    uint256 tokenId, 
    uint256 startTime, 
    uint256 expiration, 
    uint256 price, 
    uint256 quantity, 
    uint256 createdAtBlockNumber, 
    address paymentERC20) external view returns(bytes32){

        bytes32 SELLORDER_TYPEHASH = keccak256(
            "SellOrder(address seller,address contractAddress,uint256 tokenId,uint256 startTime,uint256 expiration,uint256 price,uint256 quantity,uint256 createdAtBlockNumber,address paymentERC20)"
        );
        bytes32 structHash = keccak256(abi.encode(
        SELLORDER_TYPEHASH,
        seller,
        contractAddress,
        tokenId,
        startTime,
        expiration,
        price,
        quantity,
        createdAtBlockNumber,
        paymentERC20
        ));

        return ECDSA.toTypedDataHash(DOMAIN_SEPARATOR, structHash);
    }

    function generateBuyerDigest(
    address payable buyer,
    address contractAddress,
    uint256 tokenId,
    uint256 startTime,
    uint256 expiration,
    uint256 price,
    uint256 quantity,
    address paymentERC20
    ) external view returns(bytes32){
        bytes32 BUYORDER_TYPEHASH = keccak256(
            "BuyOrder(address buyer,address contractAddress,uint256 tokenId,uint256 startTime,uint256 expiration,uint256 price,uint256 quantity,address paymentERC20)"
        );

        bytes32 structHash = keccak256(abi.encode(
        BUYORDER_TYPEHASH,
        buyer,
        contractAddress,
        tokenId,
        startTime,
        expiration,
        price,
        quantity,
        paymentERC20
        ));
        
        return ECDSA.toTypedDataHash(DOMAIN_SEPARATOR, structHash);

    }


    function recover(bytes32 digest, bytes memory signature) external view returns(address){
        return ECDSA.recover(digest,signature);
    }
}