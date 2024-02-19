import datetime

datetime_str = '2023-01-20 13:55:26'

datetime_object = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')

zeit = datetime.datetime.strftime(datetime_object, '%H:%M:%S')
print(type(datetime_object))
print(datetime_object)  # printed in default format
print(zeit)
print(type(datetime_str))