# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from key import token as token
import time
import os
import requests
import datetime
import subprocess

update_id = ''


def extractfiles(zipname, katname):
    katalog = os.getcwd() + '\\' + katname + '\\'
    system = subprocess.Popen([r"C:\Program Files\7-Zip\7z.exe", 'x', katalog + zipname, '-y', '-o' + katalog])
    aa = system.wait()
    if aa == 0:
        os.remove(katalog + zipname)
    print("code return: ", aa)
    return (system.communicate())


def returndata(milliseconds, format_date='%d.%m'):
    # Добавил 3 часа (московское время)
    tek_date = datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=milliseconds + (3 * 60 * 60 * 1000))
    return tek_date.strftime(format_date)


def savefile(stroka, dir_name, file_name):
    file_uid = stroka[stroka.rfind("=") + 1:]
    ii = 1
    # print(file_uid)
    # print(file_name)
    while ii < 10:
        ufr = requests.get(
            r'https://zakupki.gov.ru/44fz/filestore/public/1.0/download/priz/file.html',
            params={'uid': file_uid},
            headers={r'user-agent': 'my-app/0.0.1'}
        )  # делаем запрос
        # print(ufr.request.headers)
        # print(ufr.status_code)
        if ufr.status_code == 200:
            f = open(dir_name + '\\' + file_name, "wb")  # открываем файл для записи, в режиме wb
            # f=open("local.zip","wb") #открываем файл для записи, в режиме wb
            f.write(ufr.content)  # записываем содержимое в файл; как видите - content запроса
            f.close()
            # Проверяем если архив, тогда распаковываем
            if file_name.rfind('.') > 0:
                rashirenie = file_name[file_name.rfind('.') + 1:]
                if rashirenie.lower() in ['rar', 'zip', '7z']:
                    extractfiles(file_name, dir_name)
            break
        else:
            ii += 1


# print(ii)

def otvetit(chat_id, text):
    otvet = requests.get(
        r'https://api.telegram.org/bot' + token + r'/sendMessage',
        params={'chat_id': chat_id, 'text': text},
    )
    if otvet.status_code == 200:
        print('Success!')


def save_doc(regNumber):
    popitki = 1
    while popitki < 20:
        response = requests.get(
            r'https://zakupki.gov.ru/api/mobile/proxy/917/epz/order/notice/ea44/view/documents.html',
            params={'regNumber': regNumber},
            headers={r'user-agent': 'my-app/0.0.1'},
        )
        if response.status_code == 200:
            print('Success!')
            data = response.json()

            if data['data'] is None:
                return False
            nmck = data['data']['dto']['headerBlock']['nmck']
            # print('НМЦК ', nmck)
            # print(data['data']['dto']['headerBlock']['purchaseObjectName'])
            # print('Дата создания: ' ,returndata(data['data']['dto']['headerBlock']['createdDate']))
            # print('Дата изменения: ' ,returndata(data['data']['dto']['headerBlock']['changedDate']))
            expirationDate = returndata(data['data']['dto']['headerBlock']['expirationDate'])
            # print('Дата подачи заявки: ' ,expirationDate)
            # print('Дата публикации ' ,returndata(data['data']['dto']['headerBlock']['publishedDate']))
            # print('------')
            dir_name = str(int(nmck / 1000)) + 'тр. ' + "до " + expirationDate
            text_info = "Номер закупки: " + data['data']['dto']['headerBlock']['purchaseNumber'] + "\n"
            text_info += "Объект закупки: " + data['data']['dto']['headerBlock']['purchaseObjectName'] + "\n"
            text_info += "Начальная цена: " + str(nmck) + "\n"
            text_info += "Окончание подачи заявок: " + expirationDate + "\n"
            text_info += "Заказчик: " + data['data']['dto']['headerBlock']['organizationPublishName'] + "\n"
            if not os.path.isdir(dir_name):
                # print('create dir')
                os.mkdir(dir_name)
            if not data['data']['dto']['explainsDocs'] is None:
                for i in data['data']['dto']['explainsDocs']:  # разяснения
                    for ii in i['attachments']:
                        if ii['statusAttach'] == "P":
                            # print(ii['fileName'])
                            # print(ii['linkDownload'])
                            # print('------')
                            savefile(ii['linkDownload'], dir_name, ii['fileName'])

            if not data['data']['dto']['notificationChangesNotification'] is None:
                for i in data['data']['dto']['notificationChangesNotification']:  # Извешение
                    for ii in i['attachments']:
                        if ii['statusAttach'] == "P":
                            # print(ii['fileName'])
                            # print(ii['linkDownload'])
                            # print('------')
                            savefile(ii['linkDownload'], dir_name, ii['fileName'])

            if not data['data']['dto']['structuredDocumentation'] is None:
                for i in data['data']['dto']['structuredDocumentation']:  # Документация
                    for ii in i['attachments']:
                        if ii['statusAttach'] == "P":
                            # print(ii['fileName'])
                            # print(ii['linkDownload'])
                            # print('------')
                            savefile(ii['linkDownload'], dir_name, ii['fileName'])
            # Выполним второй запрос для общей информации по закупке
            popitki_info = 1
            while popitki_info < 20:
                response_info = requests.get(
                    r'https://zakupki.gov.ru/api/mobile/proxy/917/epz/order/notice/ea44/view/common-info.html',
                    params={'regNumber': regNumber},
                    headers={r'user-agent': 'my-app/0.0.1'},
                )
                if response_info.status_code == 200:
                    # Собираем нужную информацию и записываем в файл
                    data_info = response_info.json()
                    text_info += "Площадка для проведения торгов: " + data_info['data']['dto'][
                        'generalInformationOnPurchaseBlock']['nameOfElectronicPlatform'] + "\n"
                    text_info += "Дата проведения аукциона: " + returndata(data_info['data']['dto'][
                                                                               'procedurePurchaseBlock'][
                                                                               'auctionEtpDate'],
                                                                           format_date='%d.%m.%Y %H:%M') + "\n"
                    for i in data_info['data']['dto']['customerRequirementsBlock']:  # требования клиента
                        text_info += "Сроки поставки товара или завершения работы: " + i['conditionsOfContract'][
                            'deliveryTime'] + "\n"
                        for ii in i['conditionsOfContract']['deliveryPlace']:
                            text_info += "Место доставки товара, выполнения работы: " + ii + "\n"
                        text_info += "Размер обеспечения исполнения контракта: " + str(
                            i['ensuringPerformanceContract']['amountContractEnforcement']) + "р. (" + str(
                            i['ensuringPerformanceContract']['contractGrntShare']) + "%)\n"
                        text_info += "Размер обеспечения гарантийных обязательств: " + str(
                            i['warrantyObligations']['warrantyObligationsSize']) + 'р.'

                    with open(dir_name + "\\" + "Информация.txt", "w",
                              encoding='utf-8') as file:  # открываем файл для записи, в режиме w
                        file.write(text_info)  # записываем содержимое в файл;
                    return True
                else:
                    popitki_info += 1
                    time.sleep(1)
            return False
        else:
            popitki += 1
            time.sleep(1)
    return False


def main():
    global update_id
    exit_bot = False
    while True:
        try:
            response = requests.get(
                r'https://api.telegram.org/bot' + token + r'/getUpdates',
                params={'offset': update_id},
                # headers={r'user-agent': 'my-app/0.0.1'},
            )
            if response.status_code == 200:
                print('Success!')
                data = response.json()
                # data = response.text # для отладки на сайт json-парсера
                # print(data)
                update_id = ''
                if data['ok']:
                    if not data['result'] and exit_bot:
                        otvetit(chat_id, "Программа завершается")
                        break
                        pass
                    for i in data['result']:
                        if i.get('message') is None:
                            print('err format message')
                            continue
                        update_id = str(i['update_id'] + 1)  # отключил чтобы не писать каждый раз сообщения
                        chat_id = str(i['message']['from']['id'])
                        text = i['message']['text']
                        # из текста оставить только 19 цифр
                        print(text)
                        if text.lower() in ['exit', 'quit', 'выход', 'закрыть']:
                            exit_bot = True
                            continue
                        elif len(text) > 19:
                            if text.find("regNumber=") > 0:
                                text = text[text.find("=") + 1:]
                            else:
                                # print(len(text))
                                # print(text)
                                continue
                        elif len(text) < 19:
                            # print(len(text))
                            # print(text)
                            continue
                        if len(text) == 19:
                            if not text.isdigit():
                                # print(len(text))
                                # print(text)
                                continue
                            if save_doc(text):
                                otvetit(chat_id, "Скачаны документы по закупке: " + text)
                            else:
                                otvetit(chat_id, "Ошибка загрузки по закупке: " + text)
        except Exception as ex:
            print(ex)

        time.sleep(10)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
