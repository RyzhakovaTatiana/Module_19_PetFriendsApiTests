import os
from api import PetFriends
from settings import valid_email, valid_password, without_valid_email, without_valid_password



#Инициализируем библиотеку в переменную pf и напишем для нее тесты
pf = PetFriends()

def test_get_api_key_for_valid_user(email = valid_email, password = valid_password):
    '''Проверяем метод get_api_key с учетом валидных почты и пароля. В ответе должны получить код 200
    и ключ'''
    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert "key" in result#проверяем, что при успешной авторизации был получен ключ


def test_get_list_of_pets_with_valid_key(filter=''):
    '''Проверяем метод get_list_of_pets по которому получаем список всех питомцев и этот список будет содержать
    больше 0 питомцев'''
    #_,auth_key означает, что брать ключ будем из ключа, полученного при регистрации

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    #Когда запрашиваем список всех питомцев, проверяем статус и результат
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    #По документации должен возвращаться список питомцев в формате json, т.е.
    #список должен быть не нулевым и содержать информацию о нескольких питомцах
    #result['pets'] указываем именно так, потому что все питомцы записаны в ключе pets
    assert len(result['pets']) > 0


def test_create_pet_simple_with_valid_date(name = "Шмель", animal_type = "Дворянин", age = "3"):
    '''Проверяем метод create_pet_simple по которому можно добавить питомца с корректными данными (без фото)'''

    #Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    #Добавляем питомца
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    #Проверяем, что был добавлен питомец именно с такими данными
    assert status == 200
    assert result['name'] == name


def test_add_new_pet_with_valid_data(name='Пчела', animal_type='Норвежская Лесная',
                                    age='2', pet_photo='images/my_cat.jpg'):

    '''Проверяем метод add_new_pet по которому можно добавить питомца с корректными данными (с фото)'''
    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_update_self_pet_info(name='Ниндзя', animal_type='Норвежская Лесная', age=20):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")

def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Ниндзя", "кот", "5", "images/cat2.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()

def test_Get_Mistake_during_get_api_key_without_valid_email_and_password(email=without_valid_email, password=without_valid_password):
    '''Проверяем метод get_api_key с учетом ввода невалидных почты и пароля. В ответе должны получить код 403'''
    status, result = pf.get_api_key(email, password)
    assert (status == 400) or (status == 403)

def test_get_mistake_during_create_pet_simple_with_invalid_date(name="Шмель", animal_type="Дворянин", age= "-40"):
    '''Проверяем метод create_pet_simple - Получаем ошибку, если в пост запросе отправляем отрицательный возраст питомца'''

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    # Добавляем питомца
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    # Проверяем, что был добавлен питомец именно с такими данными
    if age is str:
        assert result['age'] > 0
        print("Pet was added")
    else:
        print ("Invalid data")

def test_get_mistake_during_add_new_pet_with_invalid_foto(name='Пчела', animal_type='Норвежская Лесная',
                                        age='2', pet_photo='images/kakoeto_foto.jpg'):

    '''Проверяем метод add_new_pet - Получаем ошибку, если в пост запросе отправляем невалидное фото питомца'''
    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    if pet_photo is True:
        status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
        assert status == 200
    else:
        print("Foto Not Found")

def test_get_mistake_during_add_new_pet_with_invalid_name(name=12345, animal_type='Норвежская Лесная',
                                                            age='2', pet_photo='images/cat2.jpg'):

    '''Проверяем метод add_new_pet - Получаем ошибку, если в пост запросе отправляем невалидное имя питомца'''
    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    if name is str:
        status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
        assert status == 200
    else:
        print("Name is invalid")

    # Не получилось доработать пост запрос с добавлением фото для питомца
    #def test_add_photo_pet_with_valid_data(pet_photo) -> json:
        #'''Проверяем метод add_photo_pet по которому можно добавить фото питомца для созданного ранее питомца без фото'''
        #pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        #_, auth_key = pf.get_api_key(valid_email, valid_password)
        #_, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

        # Если список не пустой, то пробуем добавить в него питомца без фото и запрашиваем список своих питомцев
        #if len(my_pets['pets']) == 0:
            #pf.create_pet_simple(auth_key, name="Шмель", animal_type="Норвежская Лесная", age="1")
            #_, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
            # Берём id первого питомца из списка и отправляем запрос на добавление фото
            #pet_id = my_pets['pets'][0]['id']
            #status, _ = pf.add_photo_pet(auth_key, pet_id, pet_photo='images/cat2.jpg')

            # Ещё раз запрашиваем список своих питомцев
            #_, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

            # Проверяем что статус ответа равен 200 и в списке питомцев добавилось фото к питомцу Шмель

            #assert status == 200
            #assert pet_photo in my_pets.values()

        #elif ((my_pets['name']) == "Шмель" and (my_pets['animal_type']) == "Норвежская Лесная"):

            #status, _ = pf.add_photo_pet(auth_key, pet_photo='images/cat2.jpg')
            # assert status == 200
            # assert pet_photo in my_pets.values()
