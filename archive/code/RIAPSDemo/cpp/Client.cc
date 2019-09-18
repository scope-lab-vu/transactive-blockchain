#include <Client.h>

namespace transactiveenergy {
   namespace components {
      
      Client::Client(_component_conf &config, riaps::Actor &actor) :
      ClientBase(config, actor) {
      }
      
      
      void Client::OnGroupMessage(const riaps::groups::GroupId& groupId,
      capnp::FlatArrayMessageReader& capnpreader, riaps::ports::PortBase* port){
         
      }
      
      Client::~Client() {
         
      }
   }
}

riaps::ComponentBase *create_component(_component_conf &config, riaps::Actor &actor) {
   auto result = new transactiveenergy::components::Client(config, actor);
   return result;
}

void destroy_component(riaps::ComponentBase *comp) {
   delete comp;
}
