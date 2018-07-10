//
// Auto-generated by edu.vanderbilt.riaps.generator.ComponenetGenerator.xtend
//
#include <SolverBase.h>

namespace transactiveenergy {
   namespace components {
      
      SolverBase::SolverBase(_component_conf &config, riaps::Actor &actor) : ComponentBase(config, actor) {
         
      }
      
      void SolverBase::DispatchMessage(capnp::FlatArrayMessageReader* capnpreader, riaps::ports::PortBase *port,std::shared_ptr<riaps::MessageParams> params) {
         auto portName = port->GetPortName();
         
         if (portName == PORT_TIMER_POLLER) {
            OnPoller(port);
         }
         
         if (portName == PORT_TIMER_SOLVE) {
            OnSolve(port);
         }
         
      }
      
      void SolverBase::DispatchInsideMessage(zmsg_t* zmsg, riaps::ports::PortBase* port) {
         //empty the header
      }
      
      bool SolverBase::SendContractAddr(capnp::MallocMessageBuilder &messageBuilder,
      ReqAddr::Builder &message) {
         //std::cout<< "SolverBase::SendContractAddr()"<< std::endl;
         return SendMessageOnPort(messageBuilder, PORT_REQ_CONTRACTADDR);
      }
      
      bool SolverBase::RecvContractAddr(RepAddr::Reader &message) {
         //std::cout<< "SolverBase::RecvContractAddr()"<< std::endl;
         auto port = GetRequestPortByName(PORT_REQ_CONTRACTADDR);
         if (port == NULL) return false;
         
         capnp::FlatArrayMessageReader* messageReader;
         
         if (port->Recv(&messageReader)){
            message = messageReader->getRoot<RepAddr>();
            return true;
         }
         return false;
      }
      
      SolverBase::~SolverBase() {
         
      }
   }
}
