'''
    A simple class to store the parsed results
    from reading the includes and keywords files.

'''

class TestFrameworkToken:
    def __init__(self, tokenString, framework, id):
        self.tokenString = tokenString
        self.framework = framework
        self.id = id
