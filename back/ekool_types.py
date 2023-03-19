class EData():
    API_URL = 'https://postikana.ekool.eu/rest/json'
    SERVER_ROOT_URL = 'https://ekool.eu/'

class AssignmentTimeframe():
    def __init__(self,raw_obj):
        self.parse(raw_obj)


    def parse(self, raw_obj):
        self.start_date = raw_obj["startDate"]
        self.end_date = raw_obj["endDate"]
        self.week_no = raw_obj["weekNo"]
        self.order_timestamp_long = raw_obj["orderTimestampLong"]

        self.assignments = []
        # Lisame kõik kodutood jarjendisse
        for event in raw_obj["eventList"]:
            event = Assignment(event)
            self.assignments.append(event)

class Assignment():
    def __init__(self, obj):
        self.raw_obj = obj
        self.parse_assignment(obj)

    def parse_assignment(self, json_obj):
        self.author = json_obj.get("authorName", None)
        self.title = json_obj.get("title", None)
        self.order_timestamp_long = json_obj.get("orderTimestampLong", None)
        self.content = json_obj.get("content", None)
        self.comments = json_obj.get("comments", None)
        self.url = json_obj.get("url",None)
        self.id = json_obj.get("id",None)
        self.is_hot = json_obj.get("isHot", None)
        self.subject_name = json_obj.get("subjectName",None)
        self.deadLine = json_obj.get("deadLine")
        self.added = json_obj.get("added")
        self.is_done = json_obj.get("isDone",None)
        self.is_test = json_obj.get("isTest", None)
        self.is_graded = json_obj.get("isGraded", None)
        self.teacher_attachments = json_obj.get("teacherAttachments", None)
        self.type_id = json_obj.get("typeId",None)

class Feed:
    def __init__(self, raw_obj):
        self.parse(raw_obj)


    def parse(self, raw_obj):
        self.feed = []
        for feed_item_raw in raw_obj:
            feeditem = FeedItem(feed_item_raw)
            # Ära lisa reklaame. Reklaamide ID on 20
            try:
              if (feeditem.item_type == 20):
                continue
            except:
              pass
            self.feed.append(FeedItem(feed_item_raw))

class FeedItem:
    def __init__(self, raw_obj):
        self.parse(raw_obj)

    def parse(self, raw_obj):
        self.raw_obj = raw_obj
        self.id = raw_obj.get("id", None)
        self.order_seq = raw_obj.get("orderSeq", None)
        self.last_modified = raw_obj.get("lastModified", None)
        self.item_type = raw_obj.get("itemType", None)
        self.action_type = raw_obj.get("actionType", None)
        self.hot = raw_obj.get("hot", None)
        self.grade_type_id = raw_obj.get("gradeTypeId", None)
        self.grade_type_additional_desc = raw_obj.get("gradeTypeAdditionalDesc", None)
        self.grade = raw_obj.get("abbr", None)
        self.title = raw_obj.get('title', None)
        self.author_name = raw_obj.get("authorName", None)
        self.lesson_date = raw_obj.get("lessonDate", None)
        self.subject_name = raw_obj.get("subjectName", None)
        self.subject_id = raw_obj.get("subjectId", None)
        self.term_name = raw_obj.get("termName", None)
        self.content = raw_obj.get("content", None)
        self.text_content = raw_obj.get("textContent", None)
        self.has_statistics = raw_obj.get("hasStatistics", None)
        self.test = raw_obj.get("test", None)
        self.amendment = raw_obj.get("amendment", None)
