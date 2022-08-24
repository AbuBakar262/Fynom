import logging
import os
import calendar
import datetime
from blockchain.models import *
from user.models import User
from user.utils import Utill


logger = logging.getLogger(__name__)


# @api_view(('GET',))
def SendEmailToWinner():
    """send email to the action winner user, to claim nft"""

    try:
        logger.info("--------------API Called-------------")
        date = datetime.datetime.utcnow()
        utc_time = calendar.timegm(date.utctimetuple())
        nfts = NFT.objects.filter(nft_sell_type="Timed Auction", end_datetime__lt=utc_time, is_listed=True, nft_status='Approved')

        if nfts:
            for nft in nfts:
                all_bids = BidOnNFT.objects.filter(nft_detail=nft.id, bid_status='Active')
                if all_bids:
                    highest_bid = all_bids.order_by('-id').first()
                    all_bids.update(bid_status='Closed')
                    # nft.is_listed = False
                    # nft.save()
                    if highest_bid and highest_bid.is_email is False:
                        user = User.objects.filter(id=highest_bid.bidder_profile.id).first()

                        if nft.user != user:
                            if user.email:
                                body = f"You are the winner of '{nft.nft_title}' NFT. You win this NFT by bidding of {highest_bid.bid_price} ETH. " \
                                       f"To visit and claim your " \
                                       f"NFT click on the given link " + os.getenv('FRONTEND_SHOW_NFT_URL') + str(nft.id)

                                data = {
                                    'subject': 'Claim Your Phynom NFT',
                                    'body': body,
                                    'to_email': user.email
                                }

                                Utill.send_email(data)

                                highest_bid.is_email = True
                                highest_bid.is_winner = True
                                highest_bid.save()
                            else:
                                highest_bid.is_winner = True
                                highest_bid.save()
                                logger.info("Email send to user for clime NFT")
                else:
                    nft.is_listed = False
                    nft.save()

                # if bid doesn't placed  by any user

                # elif nft.user == user:
                #     body = f"On your Listed '{nft.nft_title}' NFT. No bid placed by anyone. " \
                #            f"Visit your NFT and List it again by " \
                #            f"click on the given link " + os.getenv('FRONTEND_SHOW_NFT_URL') + str(nft.id)
                #
                #     data = {
                #         'subject': 'Bid Status of Your Phynom NFT',
                #         'body': body,
                #         'to_email': user.email
                #     }
                #
                #     Utill.send_email(data)
                #     nft.is_listed = False
                #     nft.save()
                #     logger.info("Email send to owner no bid placed on this NFT.")
        else:
            logger.info("No NFT is waiting for claim.")

    except Exception as e:
        logger.info(e.args[0])

