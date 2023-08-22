class OperationStack():
  def __init__(self):
    self.operations=[]

  def push(self, operation):
    self.operations.append(operation)

  def pop(self):
    self.operations = self.operations[1:]

  def clear(self):
    self.operations=[]

  def reverse(self):
    self.operations.reverse()

  def execute(self):
    for i in range(len(self.operations)):
      self.operations[len(self.operations) - i - 1].execute()

class Operation():
  def __init__(self, callback, kwargs={}):
    self.callback=callback
    self.kwargs=kwargs

  def execute(self):
    self.callback(**self.kwargs)