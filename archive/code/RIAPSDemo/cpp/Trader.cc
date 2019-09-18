#include <Trader.h>

namespace transactiveenergy {
   namespace components {
      
      Trader::Trader(_component_conf &config, riaps::Actor &actor) :
      TraderBase(config, actor) {
      }
      
      
      void Trader::OnGroupMessage(const riaps::groups::GroupId& groupId,
      capnp::FlatArrayMessageReader& capnpreader, riaps::ports::PortBase* port){
         
      }
      
      Trader::~Trader() {
         
      }
   }
}

riaps::ComponentBase *create_component(_component_conf &config, riaps::Actor &actor) {
   auto result = new transactiveenergy::components::Trader(config, actor);
   return result;
}

void destroy_component(riaps::ComponentBase *comp) {
   delete comp;
}
