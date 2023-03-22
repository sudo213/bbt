import threading
import time
import bybit

from config import desired_price


def get_key_lists():
    keys_list = []
    with open("api_keys.txt", "r") as file_:
        for row in file_:
            keys_list.append({"api_key": row.split(" ")[0], "secret_key": row.split(" ")[1]})
    return keys_list


def check_balance_and_cell(curr_api_key, curr_secret_key):
    current_client = bybit.bybit(test=False, api_key=curr_api_key, api_secret=curr_secret_key)
    arb_balance = current_client.Wallet.Wallet_getBalance(coin="MATIC").result()[0]['result']['ARB']['equity']

    print(f"На аккаунте {curr_api_key}  монет {arb_balance}  ")

    # Ждем пополнения
    while True:
        arb_balance = current_client.Wallet.Wallet_getBalance(coin="MATIC").result()[0]['result']['ARB']['equity']
        if arb_balance != 0:
            print(f"На аккаунте {curr_api_key} появились монеты  ")
            break

    while True:

        price = current_client.Market.Market_orderbook(symbol='MATICUSDT', depth=1).result()[0]['result'][0]['price']

        if price > desired_price:
            # Продаем по нужной цене
            order = client.Order.Order_new(side="Sell", symbol='MATICUSDT', order_type="Market", qty=arb_balance,
                                           time_in_force="GoodTillCancel").result()
            print(order[0]['result']['order_id'])

            print(f"Продажа {arb_balance} монет ARB в USDT на аккаунте {curr_api_key} завершена.")
            break


def main():
    threads = []
    accounts = get_key_lists()
    for account in accounts:
        thread = threading.Thread(target=check_balance_and_cell, args=(account['api_key'], account['secret_key']))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
        time.sleep(3)


if __name__ == '__main__':
    main()
