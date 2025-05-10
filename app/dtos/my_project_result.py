def clean_data(string):
    return str(string).replace("'", "")

class MyProjectResult:
    def __init__(self, row, pipeline_id):

        if row.uses_external_id:
            self.id = clean_data(row.external_id)
        else:
            self.id = clean_data(pipeline_id)

        self.name = clean_data(row.name)
        self.base_git = clean_data(row.full_name)
        self.project_language = row.language
        self.commits_count = 0
        self.numauthors = 0
        self.forks_count = int(clean_data(row.forks_count))
        self.open_issues_count = int(clean_data(row.open_issues_count))
        self.created_at = clean_data(row.created_at)
        self.pushed_at = clean_data(row.pushed_at)

    def __str__(self):
        return str(self.id) + "\n" + self.name + "\n"