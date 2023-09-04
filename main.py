from Backup import BackUp
    

if __name__ == '__main__':
    vk_token = '...'
    yandex_token = '...'
    user_id = '...'
    reserved_photos = BackUp(vk_token, user_id, yandex_token)
    reserved_photos.upload()
    print('Ваши 5 аватарок были успешно скопированы на Яндекс.Диск')


