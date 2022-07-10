# Quixotic - Exploit Analysis

[Quixotic](https://quixotic.io/) is one of the largest NFT marketplace on Optimism. On July 1 2022, a possible exploit was [reported by Apetimism](https://twitter.com/apetimism/status/1542743841735749632), which was later [confirmed by Quixotic](https://twitter.com/quixotic_io/status/1542790067130978307).

The [ExchangeV4](https://optimistic.etherscan.io/address/0x065e8a87b8f11aed6facf9447abe5e8c5d7502b6#code) contract allows the sellers to trade their NFTs with ERC20 tokens approved by the buyers. The Sellers and Buyers have to approve their NFTs and ERC20 tokens respectively in order to allow the Exchange to trade them on the behalf of their respective owners.

### Vulnerable Components

The current implementation is logically flawed as the functions `fillSellOrder`, `fillBuyOrder` & `fillDutchAuctionOrder`, only check for, either the buyer's or seller's signature to execute a trade as a consequence of which one party can complete the order without the other party's consent.

### Prerequisites
* Seller and Buyer have to approve their NFTs and ERC20 tokens respectively to Exchange
* The `paymentERC20` contract needs to be a registered token in the [PaymentERC20Registry](https://optimistic.etherscan.io/address/0x445e27a25606dad4321c7b97ef8350a9585a5c78#code) 
* The block number at which the order has been created must be greater than the block number at which the same order was cancelled before(if it was).
* The buyer must be having a sufficient balance and approved a sufficent amount of tokens to the Exchange for the trade

### Key Points
* Seller receives 97.5% of the target price, as 2.5% goes to _makerWallet(0xeC1557A67d4980C948cD473075293204F4D280fd)
* The NFT Owner can setup a royalty `Royalty Payout Rate` anywhere between 0 to 15%, which will we sent to designated payout address defined by the owner.

### Addresses Involved
* ExchangeV4: 0x065e8a87b8f11aed6facf9447abe5e8c5d7502b6
* ExchangeRegistry: 0x40A863955742dD6CFc873a7D69dc85113FA8085F
* PaymentERC20Registry: 0x445e27a25606dad4321c7b97ef8350a9585a5c78
* CancellationRegistry: 0x522149e80BCEF74DE8592A48a4698E195c38Ad37
* Attacker: 0x0A0805082EA0fc8bfdCc6218a986efda6704eFE5
* Attacker's Contract: 0xbe81eabDBD437CbA43E4c1c330C63022772C2520

### Explanation

function [fillSellOrder](https://github.com/razzor-codes/Web3-Graveyard/blob/main/contracts/Quixotic/ExchangeV4.sol#L1630-L1679) first checks whether the buyer, the seller is targetting to trade the NFT has enough funds and has given enoug allowance to the Exchange.

```Solidity
} else {
    _checkValidERC20Payment(buyer, price, paymentERC20);
}
```

After which it makes sure that the order must not had cancelled as stated in the point 3 of Prerequisites

```Solidity
require(
    cancellationRegistry.getSellOrderCancellationBlockNumber(seller, contractAddress, tokenId) < createdAtBlockNumber,
    "This order has been cancelled."
);
```
and then it moves to validate the signature
```Solidity
function _validateSellerSignature(SellOrder memory sellOrder, bytes memory signature) internal view returns (bool) {
    bytes32 SELLORDER_TYPEHASH = keccak256(
        "SellOrder(address seller,address contractAddress,uint256 tokenId,uint256 startTime,uint256 expiration,uint256 price,uint256 quantity,uint256 createdAtBlockNumber,address paymentERC20)"
    );
    bytes32 structHash = keccak256(abi.encode(
            SELLORDER_TYPEHASH,
            sellOrder.seller,
            sellOrder.contractAddress,
            sellOrder.tokenId,
            sellOrder.startTime,
            sellOrder.expiration,
            sellOrder.price,
            sellOrder.quantity,
            sellOrder.createdAtBlockNumber,
            sellOrder.paymentERC20
        ));
    bytes32 digest = ECDSA.toTypedDataHash(DOMAIN_SEPARATOR, structHash);
    address recoveredAddress = ECDSA.recover(digest, signature);
    return recoveredAddress == sellOrder.seller;
```
If the signature is validated and matches the seller's address. The Exchange proceeds with transferring the NFT from the seller to buyer
```Solidity
_transferNFT(sellOrder.contractAddress, sellOrder.tokenId, sellOrder.seller, buyer, sellOrder.quantity);
```

and the approved funds from the buyer to the seller
```Solidity
function _sendERC20PaymentsWithRoyalties(
    address contractAddress,
    address seller,
    address buyer,
    uint256 price,
    address paymentERC20
) internal {
    uint256 royaltyPayout = (royaltyRegistry.getRoyaltyPayoutRate(contractAddress) * price) / 1000;
    uint256 makerPayout = (_makerFeePerMille * price) / 1000;
    uint256 remainingPayout = price - royaltyPayout - makerPayout;
    if (royaltyPayout > 0) {
        IERC20(paymentERC20).safeTransferFrom(
            buyer,
            royaltyRegistry.getRoyaltyPayoutAddress(contractAddress),
            royaltyPayout
        );
    }
    IERC20(paymentERC20).safeTransferFrom(buyer, _makerWallet, makerPayout);
    IERC20(paymentERC20).safeTransferFrom(buyer, seller, remainingPayout);
}
```

The buyer's permission/signature was nowhere involved, taking advantage of which an attacker can sell any Fake NFT to the buyer at any given price, without the buyer's consent.

---

Similarly function [fillBuyOrder](https://github.com/razzor-codes/Web3-Graveyard/blob/main/contracts/Quixotic/ExchangeV4.sol#L1686-L1724) only checks for the buyer's signature to execute a trade.

```Solidity
function _validateBuyerSignature(BuyOrder memory buyOrder, bytes memory signature) internal view returns (bool) {
    bytes32 BUYORDER_TYPEHASH = keccak256(
        "BuyOrder(address buyer,address contractAddress,uint256 tokenId,uint256 startTime,uint256 expiration,uint256 price,uint256 quantity,address paymentERC20)"
    );
    bytes32 structHash = keccak256(abi.encode(
            BUYORDER_TYPEHASH,
            buyOrder.buyer,
            buyOrder.contractAddress,
            buyOrder.tokenId,
            buyOrder.startTime,
            buyOrder.expiration,
            buyOrder.price,
            buyOrder.quantity,
            buyOrder.paymentERC20
        ));
    bytes32 digest = ECDSA.toTypedDataHash(DOMAIN_SEPARATOR, structHash);
    address recoveredAddress = ECDSA.recover(digest, signature);
    return recoveredAddress == buyOrder.buyer;
}
```
which means, a buyer can buy/steal any approved NFT from the seller at any price or even at no price(as the end goal is to verify the buyer's signature, the buyer can choose any value for the price to buy the NFT at), without the seller's consent. 

---

Likewise, function [fillDutchAuctionOrder](https://github.com/razzor-codes/Web3-Graveyard/blob/main/contracts/Quixotic/ExchangeV4.sol#L1732-L1767) implements the same flawed logic and allows the seller to sell any NFT to buyer at any rate without the buyer's consent.

### What was missing?

The contract lacks the logic to validate whether both of the parties agree on the same parameters. For instance, if the seller wants to sell an NFT for `X` amount of tokens, the buyer must have agreed to it. This can be done by verifying both the buyer's and seller's signature for the given trade. 