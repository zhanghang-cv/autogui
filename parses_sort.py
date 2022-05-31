import os


if __name__ == '__main__':
    for file_name in os.listdir('./parses'):
        file_path = os.path.join('./parses', file_name)

        first = file_name.split('_')[1]
        second = file_name.split('_')[0]
        third = file_name.split('_')[2]

        new_file_name = first + '_' + second + '_' + third + '.json'        
        new_file_path = os.path.join('./parses', new_file_name)

        os.rename(file_path, new_file_path)