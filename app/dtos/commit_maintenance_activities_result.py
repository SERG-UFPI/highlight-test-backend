import json

class CommitMaintenanceActivitiesResult:
    def __init__(self):     
        self.hash = "" #A
        self.message = "" #B
        self.bug_fix_regex_count = 0 #C
        self.adaptive_regex_count = 0 #D
        self.adaptive_by_negation_regex_count = 0 #E
        self.perfective_regex_count = 0 #F
        self.refactor_regex_count = 0 #G
        self.is_perfective = False #H
        self.is_refactor = False #I
        self.is_adaptive = 0 #J
        self.is_adaptive_by_negation = False #K
        self.is_corrective = False #L
        self.perfective_in_text = "" #M
        self.refactor_in_text = "" #N
        self.adaptive_in_text = "" #O
        self.adaptive_by_negation_in_text = "" #P
        self.corrective_in_text = "" #Q
        
    def set_from_csv(self, row_csv):
        self.hash = row_csv[0] #A
        self.message = row_csv[1] #B
        self.bug_fix_regex_count = self.parse_int_safe(row_csv[2]) #C
        self.adaptive_regex_count = self.parse_int_safe(row_csv[3]) #D
        self.adaptive_by_negation_regex_count = self.parse_int_safe(row_csv[4]) #E
        self.perfective_regex_count = self.parse_int_safe(row_csv[5]) #F
        self.refactor_regex_count = self.parse_int_safe(row_csv[6]) #G
        self.is_perfective = self.parse_bool_safe(row_csv[7]) #H
        self.is_refactor = self.parse_bool_safe(row_csv[8]) #I
        self.is_adaptive = self.parse_int_safe(row_csv[9]) #J
        self.is_adaptive_by_negation = self.parse_bool_safe(row_csv[10]) #K
        self.is_corrective = self.parse_bool_safe(row_csv[11]) #L
        self.perfective_in_text = row_csv[12] #M
        self.refactor_in_text = row_csv[13] #N
        self.adaptive_in_text = row_csv[14] #O
        self.adaptive_by_negation_in_text = row_csv[15] #P
        self.corrective_in_text = row_csv[16] #Q

    def parse_int_safe(self, value:str):
        """
        Parse a string to an integer. If parsing fails, return 0.
        :param value:
        :return:
        """
        try:
            return int(value)
        except ValueError:
            print("Invalid input. Please enter an integer.")
            return 0

    def parse_bool_safe(self, value: str) -> bool:
        """
        Parse a string to a boolean. If parsing fails, return False.
        :param value: The input string to parse.
        :return: A boolean value.
        """
        return value.lower() in {"true", "1"}

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return json.dumps(self.__dict__)