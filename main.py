from Backup import BackUp
    

if __name__ == '__main__':
    vk_token = '...'
    yandex_token = '...'
    user_id = '...'
    reserved_photos = BackUp(vk_token, user_id, yandex_token)
    reserved_photos.download()
    print('Ваши аватарки были успешно скопированы на Яндекс.Диск')


