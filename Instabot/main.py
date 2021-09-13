from pandas import read_excel
from instabot import Bot
from time import sleep
from random import randint


def main():
    df = read_excel('likes_full_iinfundibulum.xlsx')
    settings = read_excel('settings.xlsx')
    likes_count = 1
    print(settings)

    with open("akks_number.txt", "r") as file:
        checkpoint = int(file.read())
    akks_count = checkpoint

    bot = Bot(
        max_likes_to_like=100000,
        max_likes_per_day=100000,
        min_likes_to_like=0,
        filter_users=False,
        filter_business_accounts=False,
        filter_verified_accounts=False,
        like_delay=0
    )
    bot.login(username=settings['Логин'][0], password=settings['Пароль'][0], use_cookie=False)

    for i in range(checkpoint, checkpoint + settings['Количество лайков за сессию'][0]):
        if checkpoint >= 17180:
            print('Аккаунты закончились, если вы хотите повторно пролайкать их, то в файле akks_number.txt смените число на 0')
            break
        if likes_count >= settings['Количество лайков за сессию'][0]:
            break
        akks_count += 1
        nick = df['nickname'][i]
        medias = bot.get_user_medias(nick, filtration=False)
        if len(medias) != 0:
            for c in range(0, randint(settings['Лайков на аккаунт от'][0], settings['Лайков на аккаунт до'][0])):
                if len(medias) > c:
                    bot.like(medias[c], check_media=False)
                    print(f'{likes_count} - https://www.instagram.com/{nick}/')
                    likes_count += 1
                    sleep(randint(settings['Задержка от'][0], settings['Задержка до'][0]))

        with open("akks_number.txt", "w") as file:
            file.write(str(akks_count))
            
    with open("akks_number.txt", "w") as file:
        file.write(str(akks_count))


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print('ERROR!!! Pls send screenshot to main developer)')
        print(ex)
    
    print('end of work, the program should shutdown after 15 seconds')
    sleep(15)