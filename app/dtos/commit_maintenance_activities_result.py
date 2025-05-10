import json

class CommitMaintenanceActivitiesResult:
    def __init__(self):     
        self.id = "" #A
        self.message = "" #B
        self.bug_fix_regex_count = "" #C
        self.adaptive_regex_count = "" #D
        self.adaptive_by_negation_regex_count = "" #E
        self.perfective_regex_count = "" #F
        self.refactor_regex_count = "" #G
        self.is_perfective = "" #H
        self.is_refactor = "" #I
        self.is_adaptive = "" #J
        self.is_adaptive_by_negation = "" #K
        self.is_corrective = "" #L
        self.perfective_in_text = "" #M
        self.refactor_in_text = "" #N
        self.adaptive_in_text = "" #O
        self.adaptive_by_negation_in_text = "" #P
        self.corretive_in_text = "" #Q
        
    def set_from_csv(self, row_csv): 
        #print('set_from_csv')
        #print(row_csv)
        self.id = row_csv[0] #A
        self.message = row_csv[1] #B
        self.bug_fix_regex_count = row_csv[2] #C
        self.adaptive_regex_count = row_csv[3] #D
        self.adaptive_by_negation_regex_count = row_csv[4] #E
        self.perfective_regex_count = row_csv[5] #F
        self.refactor_regex_count = row_csv[6] #G
        self.is_perfective = row_csv[7] #H
        self.is_refactor = row_csv[8] #I
        self.is_adaptive = row_csv[9] #J
        self.is_adaptive_by_negation = row_csv[10] #K
        self.is_corrective = row_csv[11] #L
        self.perfective_in_text = row_csv[12] #M
        self.refactor_in_text = row_csv[13] #N
        self.adaptive_in_text = row_csv[14] #O
        self.adaptive_by_negation_in_text = row_csv[15] #P
        self.corretive_in_text = row_csv[16] #Q
        
    def __str__(self):
        return json.dumps(self.__dict__)