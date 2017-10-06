# deployment
DSO_ADDRESS = 'tcp://127.0.0.1:10001'
DATA_PATH = "data/"
TRANSACTION_GAS = "0x100000000"
BYTECODE = "0x606060405260016000806101000a81548167ffffffffffffffff021916908367ffffffffffffffff1602179055506161a8600060086101000a81548167ffffffffffffffff021916908367ffffffffffffffff160217905550614e20600060106101000a81548167ffffffffffffffff021916908367ffffffffffffffff1602179055506000600360006101000a81548167ffffffffffffffff021916908367ffffffffffffffff1602179055506000600560006101000a81548167ffffffffffffffff021916908367ffffffffffffffff1602179055506000600760006101000a81548167ffffffffffffffff021916908367ffffffffffffffff160217905550341561010c57600080fd5b6116dc8061011b6000396000f30060606040526000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff1680638375ced0146100695780639e52b99f146100cf578063b8e7a7fb14610148578063c37df44e14610188578063f5757421146101ee57600080fd5b341561007457600080fd5b6100cd600480803567ffffffffffffffff1690602001909190803567ffffffffffffffff1690602001909190803567ffffffffffffffff1690602001909190803567ffffffffffffffff1690602001909190505061022b565b005b34156100da57600080fd5b610146600480803567ffffffffffffffff1690602001909190803567ffffffffffffffff1690602001909190803567ffffffffffffffff1690602001909190803567ffffffffffffffff1690602001909190803567ffffffffffffffff1690602001909190505061049a565b005b341561015357600080fd5b610186600480803567ffffffffffffffff1690602001909190803567ffffffffffffffff16906020019091905050611186565b005b341561019357600080fd5b6101ec600480803567ffffffffffffffff1690602001909190803567ffffffffffffffff1690602001909190803567ffffffffffffffff1690602001909190803567ffffffffffffffff169060200190919050506111d8565b005b34156101f957600080fd5b610201611447565b604051808267ffffffffffffffff1667ffffffffffffffff16815260200191505060405180910390f35b8167ffffffffffffffff168367ffffffffffffffff161115151561024e57600080fd5b7fb0f09a7c285d588112f109144f5e334575b9cd0a6b1ec1c0a5ca6949ab815000600560009054906101000a900467ffffffffffffffff1685858585604051808667ffffffffffffffff1667ffffffffffffffff1681526020018567ffffffffffffffff1667ffffffffffffffff1681526020018467ffffffffffffffff1667ffffffffffffffff1681526020018367ffffffffffffffff1667ffffffffffffffff1681526020018267ffffffffffffffff1667ffffffffffffffff1681526020019550505050505060405180910390a16080604051908101604052808567ffffffffffffffff1681526020018467ffffffffffffffff1681526020018367ffffffffffffffff1681526020018267ffffffffffffffff16815250600460006005600081819054906101000a900467ffffffffffffffff168092919060010191906101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555067ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060008201518160000160006101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555060208201518160000160086101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555060408201518160000160106101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555060608201518160000160186101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555090505050505050565b600080600080600760009054906101000a900467ffffffffffffffff1667ffffffffffffffff168967ffffffffffffffff161015156104d857600080fd5b600560009054906101000a900467ffffffffffffffff1667ffffffffffffffff168867ffffffffffffffff1610151561051057600080fd5b600360009054906101000a900467ffffffffffffffff1667ffffffffffffffff168767ffffffffffffffff1610151561054857600080fd5b600460008967ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060000160089054906101000a900467ffffffffffffffff1667ffffffffffffffff168667ffffffffffffffff16101515156105a957600080fd5b600460008967ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060000160109054906101000a900467ffffffffffffffff1667ffffffffffffffff168667ffffffffffffffff161115151561060a57600080fd5b600260008867ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060000160089054906101000a900467ffffffffffffffff1667ffffffffffffffff168667ffffffffffffffff161015151561066b57600080fd5b600260008867ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060000160109054906101000a900467ffffffffffffffff1667ffffffffffffffff168667ffffffffffffffff16111515156106cc57600080fd5b600660008a67ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002093506000809054906101000a900467ffffffffffffffff168502925060016000600460008b67ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060000160009054906101000a900467ffffffffffffffff1667ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060009054906101000a900467ffffffffffffffff16915060016000600260008a67ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060000160009054906101000a900467ffffffffffffffff1667ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060009054906101000a900467ffffffffffffffff169050828460020160008a67ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060008282829054906101000a900467ffffffffffffffff160192506101000a81548167ffffffffffffffff021916908367ffffffffffffffff160217905550828460030160008967ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060008282829054906101000a900467ffffffffffffffff160192506101000a81548167ffffffffffffffff021916908367ffffffffffffffff160217905550848460040160008467ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060008867ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060008282829054906101000a900467ffffffffffffffff160192506101000a81548167ffffffffffffffff021916908367ffffffffffffffff160217905550848460050160008367ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060008867ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060008282829054906101000a900467ffffffffffffffff160192506101000a81548167ffffffffffffffff021916908367ffffffffffffffff160217905550600460008967ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060000160189054906101000a900467ffffffffffffffff1667ffffffffffffffff168460020160008a67ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060009054906101000a900467ffffffffffffffff1667ffffffffffffffff1611151515610a9357600080fd5b600260008867ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060000160189054906101000a900467ffffffffffffffff1667ffffffffffffffff168460030160008967ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060009054906101000a900467ffffffffffffffff1667ffffffffffffffff1611151515610b3157600080fd5b600060089054906101000a900467ffffffffffffffff1667ffffffffffffffff168460040160008467ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060008867ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060009054906101000a900467ffffffffffffffff1667ffffffffffffffff1611151515610bcc57600080fd5b600060089054906101000a900467ffffffffffffffff1667ffffffffffffffff168460050160008367ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060008867ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060009054906101000a900467ffffffffffffffff1667ffffffffffffffff1611151515610c6757600080fd5b600060109054906101000a900467ffffffffffffffff1667ffffffffffffffff168460050160008467ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060008867ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060009054906101000a900467ffffffffffffffff168560040160008567ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060008967ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060009054906101000a900467ffffffffffffffff160367ffffffffffffffff1611151515610d6657600080fd5b600060109054906101000a900467ffffffffffffffff1667ffffffffffffffff168460050160008367ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060008867ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060009054906101000a900467ffffffffffffffff168560050160008467ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060008967ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060009054906101000a900467ffffffffffffffff160367ffffffffffffffff1611151515610e6557600080fd5b6080604051908101604052808967ffffffffffffffff1681526020018867ffffffffffffffff1681526020018767ffffffffffffffff1681526020018667ffffffffffffffff1681525084600001600086600101600081819054906101000a900467ffffffffffffffff168092919060010191906101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555067ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060008201518160000160006101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555060208201518160000160086101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555060408201518160000160106101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555060608201518160000160186101000a81548167ffffffffffffffff021916908367ffffffffffffffff160217905550905050848460010160088282829054906101000a900467ffffffffffffffff160192506101000a81548167ffffffffffffffff021916908367ffffffffffffffff160217905550600860010160089054906101000a900467ffffffffffffffff1667ffffffffffffffff168460010160089054906101000a900467ffffffffffffffff1667ffffffffffffffff1611156110fc578360086001820160009054906101000a900467ffffffffffffffff168160010160006101000a81548167ffffffffffffffff021916908367ffffffffffffffff1602179055506001820160089054906101000a900467ffffffffffffffff168160010160086101000a81548167ffffffffffffffff021916908367ffffffffffffffff1602179055509050505b7f15640476521fd414bd504b67b615bbd406c0147e66a8b99bc4c6e79d85686593898560010160089054906101000a900467ffffffffffffffff16604051808367ffffffffffffffff1667ffffffffffffffff1681526020018267ffffffffffffffff1667ffffffffffffffff1681526020019250505060405180910390a1505050505050505050565b80600160008467ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060006101000a81548167ffffffffffffffff021916908367ffffffffffffffff1602179055505050565b8167ffffffffffffffff168367ffffffffffffffff16111515156111fb57600080fd5b7f47be5dd1d9aeb3db0a9753c2d318b0140db2a5524856bd0b17bd92b4b1da8ede600360009054906101000a900467ffffffffffffffff1685858585604051808667ffffffffffffffff1667ffffffffffffffff1681526020018567ffffffffffffffff1667ffffffffffffffff1681526020018467ffffffffffffffff1667ffffffffffffffff1681526020018367ffffffffffffffff1667ffffffffffffffff1681526020018267ffffffffffffffff1667ffffffffffffffff1681526020019550505050505060405180910390a16080604051908101604052808567ffffffffffffffff1681526020018467ffffffffffffffff1681526020018367ffffffffffffffff1681526020018267ffffffffffffffff16815250600260006003600081819054906101000a900467ffffffffffffffff168092919060010191906101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555067ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060008201518160000160006101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555060208201518160000160086101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555060408201518160000160106101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555060608201518160000160186101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555090505050505050565b60007f25346e016c4cdf007ed72a549d9e82213a82d4f742035bfe48286948ed7ab4e7600760009054906101000a900467ffffffffffffffff16604051808267ffffffffffffffff1667ffffffffffffffff16815260200191505060405180910390a16040805190810160405280600067ffffffffffffffff168152602001600067ffffffffffffffff1681525060066000600760009054906101000a900467ffffffffffffffff1667ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060008201518160010160006101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555060208201518160010160086101000a81548167ffffffffffffffff021916908367ffffffffffffffff1602179055509050506000600760009054906101000a900467ffffffffffffffff1667ffffffffffffffff1614156116655760066000600760009054906101000a900467ffffffffffffffff1667ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060086001820160009054906101000a900467ffffffffffffffff168160010160006101000a81548167ffffffffffffffff021916908367ffffffffffffffff1602179055506001820160089054906101000a900467ffffffffffffffff168160010160086101000a81548167ffffffffffffffff021916908367ffffffffffffffff1602179055509050505b6007600081819054906101000a900467ffffffffffffffff168092919060010191906101000a81548167ffffffffffffffff021916908367ffffffffffffffff1602179055509050905600a165627a7a72305820d5d8c661ca601eb6a4d555093ab035822bbc9fb0754c3073e030497d852dd2ba0029"

SOLVING_INTERVAL = 10 # seconds
FINALIZING_INTERVAL = 60 # seconds

# model
FEEDERS = []
PROSUMERS = []
PROSUMER_FEEDER = {}
for (feeder, num_prosumers) in [(1, 9), (2, 17), (3, 5), (4, 13), (5, 8), (6, 1), (7, 10), (8, 17), (9, 5), (10, 13), (11, 4)]:
  FEEDERS.append(feeder)
  for prosumer in range(1, num_prosumers + 1):
    prosumer_id = feeder * 100 + prosumer
    PROSUMERS.append(prosumer_id)
    PROSUMER_FEEDER[prosumer_id] = feeder

from Microgrid import Microgrid
MICROGRID = Microgrid(
  interval_length=1.0, 
  C_ext=20000, 
  C_int=25000, 
  feeders=FEEDERS, 
  prosumer_feeder=PROSUMER_FEEDER)
  

