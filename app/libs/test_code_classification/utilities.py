import csv

from app.libs.test_code_classification.TestFrameworkToken import TestFrameworkToken

def lookup_generator(filename):
    """
        lookupGenerator parses a file to create a lookup table 
        based on the contents of the file.
    
        Parameters: filename - String representing the path to the file
        Returns: A dictionary representing the file's contents
        
        Note: The contents of the file pointed to by filename must 
              be in the form of: 
          
              token0,token1
    """
    lookup = {}
    for line in open(filename):
        if line != "":
            line = line.strip("\n")
            tokens = line.split(",")
            language = tokens[0]
            tokenString = tokens[1]
            
            if tokens[0] not in lookup:
                lookup[language] = [tokenString]
            else:
                lookup[language] += [tokenString]
    #print(lookup)
    return lookup
    
def tech_lookup_generator(filename):
    """
        techLookupGenerator parses a file (testingTechnologies.csv) 
        to create a lookup table based on the contents of the file.
    
        Parameters: filename - String representing the path to the file
        Returns: A dictionary representing the file's contents
        
        Note: The contents of the file pointed to by filename must 
              be in the form of: 
          
              token0,token1,token2,token3
    """
    print("Creating Test Framework Dictionary...")
    lookup = {}
    count = 1
    for line in csv.reader(open(filename)):
        if count != 1:
            langId = line[0]
            langauge = line[1]
            tokenString = line[2]
            framework = line[3]
            testToken = TestFrameworkToken(tokenString, framework, langId)
            if langauge not in lookup:
                lookup[langauge] = [testToken]
            else:
                lookup[langauge] += [testToken]
        count += 1
    #print(lookup)
    return lookup
