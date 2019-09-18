#include <DSO.h>

namespace transactiveenergy {
   namespace components {
      
      DSO::DSO(_component_conf &config, riaps::Actor &actor) :
      DSOBase(config, actor) {
      }
      
      void DSO::OnClock(riaps::ports::PortBase *port) {
         std::cout << "DSO::OnClock(): " << port->GetPortName() << std::endl;
      }
      
      void DSO::OnTrader(const ReqAddr::Reader &message,
      riaps::ports::PortBase *port)
      {
         std::cout<< "DSO::OnTrader()"<< std::endl;
      }
      
      void DSO::OnGroupMessage(const riaps::groups::GroupId& groupId,
      capnp::FlatArrayMessageReader& capnpreader, riaps::ports::PortBase* port){
         
      }
      
      DSO::~DSO() {
         
      }
   }
}

riaps::ComponentBase *create_component(_component_conf &config, riaps::Actor &actor) {
   auto result = new transactiveenergy::components::DSO(config, actor);
   return result;
}

void destroy_component(riaps::ComponentBase *comp) {
   delete comp;
}
