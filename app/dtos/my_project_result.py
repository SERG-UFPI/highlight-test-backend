
class MyProjectResult:
    def __init__(self, row, pipeline_id):

        self.id = self.clean_data(pipeline_id)
        self.name = self.clean_data(row.name)
        self.base_git = self.clean_data(row.full_name)
        self.project_language = row.language
        self.commits_count = 0
        self.numauthors = 0
        self.forks_count = int(self.clean_data(row.forks_count))
        self.open_issues_count = int(self.clean_data(row.open_issues_count))
        self.created_at = self.clean_data(row.created_at)
        self.pushed_at = self.clean_data(row.pushed_at)

    def clean_data(self, string):
        """
        Clean the input string by removing single quotes.
        :param string:
        :return:
        """
        return str(string).replace("'", "")

    def __str__(self):
        return str(self.id) + "\n" + self.name + "\n"