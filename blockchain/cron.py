import logging
import os
from rest_framework.response import Response
from rest_framework import status
from blockchain.models import *
from user.models import User
from user.utils import Utill
# from rest_framework.decorators import api_view
# from backend.settings import *

logger = logging.getLogger(__name__)

# @api_view(('GET',))
def SendEmailToWinner():
    """send email to the action winner user, to claim nft"""

    # try:
    logger.info("good 1")
    user_wallet_no = 'newuser'
    nft_token_id = '123456789'
    price = '0.35895'
    logger.info("good 2")
    user = User.objects.all()
    wallet_info = UserWalletAddress.objects.filter(wallet_address=user_wallet_no).first()
    logger.info("good 3")
    user = User.objects.filter(id=wallet_info.user_wallet.id).first()
    logger.info("good 4")
    nft = NFT.objects.filter(token_id=nft_token_id).first() #nft.nft_title
    logger.info("good 5")

    if user.email:
        body = f"You are the winner of '{nft.nft_title}' NFT. You win this NFT by bidding of {price} ETH. " \
               f"To visit and claim your " \
               f"NFT click on the given link " + os.getenv('FRONTEND_SHOW_NFT_URL') + str(nft.id)
        logger.info("good 6")
        data = {
            'subject': 'Claim Your Phynom NFT',
            'body': body,
            'to_email': user.email
        }
        logger.info("good 7")
        Utill.send_email(data)
        logger.info("good 8")
        return Response({
            "status": True, "status_code": 200, 'msg': 'Email sent to the user for claim NFT.',
            "data": []}, status=status.HTTP_200_OK)
    logger.info("good 9")
    return Response({
        "status": True, "status_code": 200, 'msg': 'Your email not found.',
        "data": []}, status=status.HTTP_200_OK)


    # except Exception as e:
    #     return Response({
    #         "status": False, "status_code": 400, 'msg': e.args[0],
    #         "data": []}, status=status.HTTP_400_BAD_REQUEST)
