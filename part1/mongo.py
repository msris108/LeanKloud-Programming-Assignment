import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["workspace"]
mycol = mydb["todos"]

# id = 3
# x = mycol.find_one({"_id" : id})
# y = mycol.count_documents({})
# z = mycol.find().count()

# _id  = 1
# data = {'$set': {"task": "Task 1", "status": "Not Started", "date" : "2021-05-25"}}
# x = mycol.update_one({"_id" : _id}, data)

# print(x.id)

# status = ["Finished", "Not Started"]

# myquery = { "status": { "$regex": "Not Started|Finished" } }

todo_list = []
todos = mycol.find({ "status": { "$regex": "Not Started|Finished" } })
for todo in todos:
	todo_list.append(todo)

print(todo_list)
