class Auth:

    def __init__(self, path_to_token_file):
        with open(path_to_token_file, 'r') as file:
            for line in file:
                spl_line = line.split(',')
                if spl_line[0] == 'community_token':
                    self.community_token = spl_line[1].strip()
                else:
                    self.user_token = spl_line[1].strip()
        self.community_id = -167621445
        self.user_id = 491551942