from werkzeug.security import generate_password_hash

password = input(str('Enter Password: '))
password_hash = generate_password_hash(password)
print(password_hash)

