from . import rdflogging

class CallWrapper:
    def __init__(self, parent_w, o, method_name, method_o):
        self.parent_w = parent_w
        self.o = o        
        self.method_name = method_name
        self.method_o = method_o

    def __call__(self, *args, **kwargs):
        #ipdb.set_trace()
        mc_is_active = self.parent_w.parent_mc.is_active
        if mc_is_active:
            chained_call_name = self.parent_w.parent_mc.mc_name
            o_id = id(self.o)
            ret = self.method_o(*args, **kwargs)
            ret_id = id(ret)            
            print("__call__ ", chained_call_name, o_id, self.method_name, args, kwargs, ret_id)
            
            if rdflogging.rdflogger:
                methods_chain_id = id(self.parent_w.parent_mc)
                method_call_id = id(self)

                o_uri = rdflogging.rdflogger.register_obj(o_id)
                ret_uri = rdflogging.rdflogger.register_obj(ret_id)
                methods_chain_uri = rdflogging.rdflogger.register_methods_chain(methods_chain_id)
                method_call_uri = f"<pyjviz:MethodCall:{method_call_id}>"

                rdflogging.rdflogger.dump_triple__(method_call_uri, "rdf:type", "<pyjviz:MethodCall>")
                rdflogging.rdflogger.dump_triple__(method_call_uri, "rdf:label", f'"{self.method_name}"')
                #rdflogging.rdflogger.dump_triple__(f"<pyjviz:method-call:{method_call_id}>", "<pyjviz:Thread>", f'"{get_thread_id()}"')
                rdflogging.rdflogger.dump_triple__(method_call_uri, "<pyjviz:belongs-to-methods-chain>", methods_chain_uri)
                rdflogging.rdflogger.dump_triple__(method_call_uri, "<pyjviz:method-call-arg0>", o_uri)
                rdflogging.rdflogger.dump_triple__(method_call_uri, "<pyjviz:method-call-return>", ret_uri)

                """
                for arg in args:
                    arg_id = id(arg)
                    arg_uri = rdflogging.rdflogger.register_obj(arg_id)
                    rdflogging.rdflogger.dump_triple__(method_call_uri, "rdf:type", "<pyjviz:MethodCall>")
                """
                
            ret = Wrapper(ret, self.parent_w.parent_mc)
        else:
            ret = Wrapper(self.method_o(*args, **kwargs), self.parent_w.parent_mc)
            
        return ret

class Wrapper:
    def __init__(self, o, parent_mc):
        self.o = o
        self.parent_mc = parent_mc

    def __getattr__(self, attr):
        o = self.__getattribute__('o')
        method_name = attr
        method_o = getattr(o, method_name)
        return CallWrapper(self, o, method_name, method_o)

    def __str__(self):
        o = self.__getattribute__('o')
        return str(o)
    
class MethodsChain:
    def __init__(self, mc_name):
        self.is_active = False
        self.mc_name = mc_name

        if rdflogging.rdflogger:
            rdflogging.rdflogger.dump_methods_chain_creation(id(self), mc_name)
        
    def __enter__(self):
        self.is_active = True
        print(f"enter methods chain {self.mc_name}")
        return self

    def __exit__(self, type, value, traceback):
        self.is_active = False
        print(f"exit methods chain {self.mc_name}")

    def __del__(self):
        print(f"deleting methods chain {self.mc_name} {id(self)}")
        
    def head(self, mc_head_obj):
        print("head id:", id(mc_head_obj))
        return Wrapper(mc_head_obj, self)
