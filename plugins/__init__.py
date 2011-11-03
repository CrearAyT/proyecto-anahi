class SinkTest(object):
    name = 'Volcar datos a stdout'

    def __init__(self):
        pass

    def new_data(self, data, *args, **kwargs):
        print 'sink ', data
    
    def start(self):
        print 'sink start'

    def stop(self):
        print 'sink stop'

    def destroy(self):
        print 'sink destroy'
