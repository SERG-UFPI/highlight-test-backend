import re

# def directoryVote(pattern, file):
#     """
#         directoryVote determines if a file is located in a 'test' directory
#         and returns a 1 if it is in a test directory and a 0 otherwise
         
#         Parameters: pattern - Regex pattern for determining a test directory
#                     file - Path object representing a path to a file
#         Return: 0 or 1 if the file is in a test directory
#     """
#     match = pattern.match(re.escape(str(file.parent)))
    
#     if(match):
#         return 1
#     else:
#         return 0

# def filenameVote(pattern, file):
#     """
#         directoryVote determines if a file is located in a 'test' directory
#         and returns a 1 if it is in a test directory and a 0 otherwise
         
#         Parameters: pattern - Regex pattern for determining a test directory
#                     file - Path object representing a path to a file
#         Return: 0 or 1 if the file is in a test directory
#     """
#     match = pattern.match(str(file.name))
    
#     if(match):
#         return 1
#     else:
#         return 0
    
def test_include(testLookup, fileExtension, fileContents):
    """
        testIncludeVote determines if a file references a testing framework within
        it and returns a 1 if that is the case and a 0 otherwise
        
        Parameters: includeLookup - dictionary that stores the test framework 
                    reference by file extension
                    file - Path object representing a path to a file
        Return: 0 or 1 if the file contains a reference to a test framework
    """
    includeList = testLookup[fileExtension]
    for includeToken in includeList:
        #print(includeToken.tokenString)
        includePattern = re.compile(includeToken.tokenString)
        match = includePattern.search(fileContents, re.IGNORECASE|re.MULTILINE)
        
        if(match):
            #print("match: " + str(includeToken.framework))
            return 1
        
    return 0

def test_keyword(keywordLookup, fileExtension, fileContents):
    """
        testIncludeVote determines if a file references a testing framework within
        it and returns a 1 if that is the case and a 0 otherwise
        
        Parameters: keywordLookup - dictionary that stores the keywords 
                    by file extension
                    file - Path object representing a path to a file
        Return: 0 or 1 if the file contains a keyword
    """
    if (fileExtension in keywordLookup):
        keywordList = keywordLookup[fileExtension]

        for keyword in keywordList:
            keywordPattern = re.compile(keyword)
            match = keywordPattern.search(fileContents, re.IGNORECASE|re.MULTILINE)
            if(match):
                return 1
            
    return 0
    
def findTestTechs(techLookup, fileExtension, fileContents):
    """
        findTestTechs finds all of the testing techonologies that a
        particular file uses
        
        Parameters: techLookup - dictionary that stores the test framework 
                    reference by file extension
                    file - Path object representing a path to a file
        Return: A list containing references to the TestFrameworkToken objects
                that were matched in the file
    """
    techList = techLookup[fileExtension]
    matchedTechs = []

    for testToken in techList:
        #print(testToken.tokenString)
        
        techPattern = re.compile(testToken.tokenString)
        match = techPattern.search(fileContents, re.IGNORECASE|re.MULTILINE)
        
        #print(testToken.tokenString, fileContents)
        
        if(match):
            matchedTechs += [testToken.tokenString]
                
    return matchedTechs

def findKeywordTechs(keywordLookup, fileExtension, fileContents):
    """
        findKeywordTechs finds all of the testing keywords that a
        particular file uses
        
        Parameters: keywordLookup - dictionary that stores the keywords 
                    by file extension
                    file - Path object representing a path to a file
        Return: A list containing references to the Keywords objects
                that were matched in the file
    """
    matchedKeywords = []
    if (fileExtension in keywordLookup):
        keywordList = keywordLookup[fileExtension]
        

        for keyword in keywordList:
            keywordPattern = re.compile(keyword)
            match = keywordPattern.search(fileContents, re.IGNORECASE|re.MULTILINE)
            if(match):
                matchedKeywords += [keyword]
            
    return matchedKeywords
