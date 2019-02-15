import paypalrestsdk
from wechatpy import WeChatClient
from wechatpy.pay.api import WeChatOrder
from alipay import AliPay


class Pay:
    def __init__(self, config, sandbox=True):
        self._paypal = paypalrestsdk.Api({
            "mode":
            "sandbox" if sandbox else "live",
            "client_id":
            config.get("PAYPAL_ID"),
            "client_secret":
            config.get("PAYPAL_SECRET")
        })
        self._alipay = AliPay(
            config.get("ALIPAY_ID"),
            app_notify_url=config.get("ALIPAY_NOTIFY_URL"),
            app_private_key_string=config.get("ALIPAY_PRIVATE_KEY"),
            alipay_public_key_string=config.get("ALIPAY_PUBLIC_KEY"),
            sign_type="RSA",
            debug=sandbox)
        self._wechat = WeChatOrder(
            WeChatClient(config.get("WECHAT_ID"), config.get("WECHAT_SECRET")))
        self._config = config

    def create_payment(self,
                       method,
                       amount_total,
                       description=None,
                       product_id=None):
        if method == "paypal":
            payment = paypalrestsdk.Payment(
                {
                    "intent":
                    "sale",

                    # Set payment method
                    "payer": {
                        "payment_method": "paypal"
                    },

                    # Set redirect URLs
                    "redirect_urls": {
                        "return_url": self._config.get("PAYPAL_RETURN_URL"),
                        "cancel_url": self._config.get("PAYPAL_CANCEL_URL")
                    },

                    # Set transaction object
                    "transactions": [{
                        "amount": {
                            "total": amount_total,
                            "currency": "USD"
                        },
                        "description": description
                    }]
                },
                api=self._paypal)
            if payment.create():
                return payment
            else:
                return None
        if method == "wechat":
            payment = self._wechat.create(
                "NATIVE",
                description,
                amount_total,
                self._config.get("WECHAT_NOTIFY_URL"),
                self._config.get("WECHAT_CLIENT_IP"),
                product_id=product_id,
                device_info="WEB")
            return payment
        if method == "alipay":
            order_string = self._alipay.api_alipay_trade_page_pay(
                out_trade_no=product_id,
                total_amount=amount_total,
                subject=description,
                return_url=self._config.get("ALIPAY_RETURN_URL"))
            url = "https://openapi.alipay.com/gateway.do?" + order_string
            return url
