//
// Auto-generated by edu.vanderbilt.riaps.generator.ComponenetGenerator.xtend
//
#include <DSOBase.h>

namespace transactiveenergy {
   namespace components {
      
      DSOBase::DSOBase(_component_conf &config, riaps::Actor &actor) : ComponentBase(config, actor) {
         
      }
      
      void DSOBase::DispatchMessage(capnp::FlatArrayMessageReader* capnpreader, riaps::ports::PortBase *port,std::shared_ptr<riaps::MessageParams> params) {
         auto portName = port->GetPortName();
         if (portName == PORT_REP_CONTRACTADDR) {
            auto reader = capnpreader->getRoot<ReqAddr>();
            OnContractAddr(reader, port);
         }
         
         if (portName == PORT_TIMER_FINALIZER) {
            OnFinalizer(port);
         }
         
      }
      
      void DSOBase::DispatchInsideMessage(zmsg_t* zmsg, riaps::ports::PortBase* port) {
         //empty the header
      }
      
      bool DSOBase::SendContractAddr(capnp::MallocMessageBuilder& messageBuilder,
      RepAddr::Builder& message) {
         std::cout<< "DSOBase::SendContractAddr()"<< std::endl;
         return SendMessageOnPort(messageBuilder, PORT_REP_CONTRACTADDR);
      }
      
      DSOBase::~DSOBase() {
         
      }
   }
}
