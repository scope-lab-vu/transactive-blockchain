#include <Solver.h>

namespace transactiveenergy {
   namespace components {
      
      Solver::Solver(_component_conf &config, riaps::Actor &actor) :
      SolverBase(config, actor) {
      }
      
      
      void Solver::OnGroupMessage(const riaps::groups::GroupId& groupId,
      capnp::FlatArrayMessageReader& capnpreader, riaps::ports::PortBase* port){
         
      }
      
      Solver::~Solver() {
         
      }
   }
}

riaps::ComponentBase *create_component(_component_conf &config, riaps::Actor &actor) {
   auto result = new transactiveenergy::components::Solver(config, actor);
   return result;
}

void destroy_component(riaps::ComponentBase *comp) {
   delete comp;
}
