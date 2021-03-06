import tornado
import json

import decorators, db
import handlers.base as base

class UsersInfo(base.BaseHandler):
    
    ITEMS_PER_PAGE = 100
    
    @tornado.web.authenticated
    @decorators.requestAdmin
    @tornado.web.asynchronous
    def get(self):
        start = int(self.get_argument(u'p', 0))
                
        database = db.DataBase()
        users = database.paginate_users(start, self.ITEMS_PER_PAGE)
        self.finish(json.dumps(users))
                

class UserSetRights(base.BaseHandler):
    
    @tornado.web.authenticated
    @decorators.requestAdmin
    @tornado.web.asynchronous
    def put(self):
        user_id = int(self.get_argument(u'id', -1))
        if user_id < 0:
            raise tornado.web.HTTPError(400)
        
        new_rights = int(self.get_argument(u'v', -1))
        if new_rights < 0 or new_rights > 255:
            raise tornado.web.HTTPError(400)
        
        if self.current_user.rights < new_rights:
            raise tornado.web.HTTPError(400)
        
        database = db.DataBase()
        u = database.get_user_by_id(user_id)
        if not u:
            raise tornado.web.HTTPError(500)
        
        r = database.get_user_rights(u)
        if not r:
            raise tornado.web.HTTPError(500)
        
        if r.rights > self.current_user.rights:
            raise tornado.web.HTTPError(400)
        
        u.role = new_rights
        database.update_user(u)
        
        self.finish(json.dumps({'id': u.id, 
                                'role': 
                                {
                                    'value': u.role,
                                    'name': database.get_rights_by_id(u.role).name
                                }
                               }))
        
class UserListRights(base.BaseHandler):
    
    @tornado.web.authenticated
    @decorators.requestAdmin
    @tornado.web.asynchronous
    def get(self):
        database = db.DataBase()
        self.finish(json.dumps(list(map(lambda r: {'value': r.rights, 'name': r.name}, database.list_rights()))))
        