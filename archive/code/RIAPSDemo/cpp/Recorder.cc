#include <Recorder.h>

namespace transactiveenergy {
   namespace components {
      
      Recorder::Recorder(_component_conf &config, riaps::Actor &actor) :
      RecorderBase(config, actor) {
      }
      
      
      void Recorder::OnPoller(riaps::ports::PortBase *port) {
         std::cout << "Recorder::OnPoller(): " << port->GetPortName() << std::endl;
      }
      
      void Recorder::OnGroupMessage(const riaps::groups::GroupId& groupId,
      capnp::FlatArrayMessageReader& capnpreader, riaps::ports::PortBase* port){
         
      }
      
      Recorder::~Recorder() {
         
      }
   }
}

riaps::ComponentBase *create_component(_component_conf &config, riaps::Actor &actor) {
   auto result = new transactiveenergy::components::Recorder(config, actor);
   return result;
}

void destroy_component(riaps::ComponentBase *comp) {
   delete comp;
}
