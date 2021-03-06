// Generated by the gRPC C++ plugin.
// If you make any local change, they will be lost.
// source: dealer.proto

#include "dealer.pb.h"
#include "dealer.grpc.pb.h"

#include <grpc++/impl/codegen/async_stream.h>
#include <grpc++/impl/codegen/async_unary_call.h>
#include <grpc++/impl/codegen/channel_interface.h>
#include <grpc++/impl/codegen/client_unary_call.h>
#include <grpc++/impl/codegen/method_handler_impl.h>
#include <grpc++/impl/codegen/rpc_service_method.h>
#include <grpc++/impl/codegen/service_type.h>
#include <grpc++/impl/codegen/sync_stream.h>
namespace Dealer {

static const char* Game_method_names[] = {
  "/Dealer.Game/GameStream",
};

std::unique_ptr< Game::Stub> Game::NewStub(const std::shared_ptr< ::grpc::ChannelInterface>& channel, const ::grpc::StubOptions& options) {
  std::unique_ptr< Game::Stub> stub(new Game::Stub(channel));
  return stub;
}

Game::Stub::Stub(const std::shared_ptr< ::grpc::ChannelInterface>& channel)
  : channel_(channel), rpcmethod_GameStream_(Game_method_names[0], ::grpc::RpcMethod::BIDI_STREAMING, channel)
  {}

::grpc::ClientReaderWriter< ::Dealer::DealerRequest, ::Dealer::DealerRequest>* Game::Stub::GameStreamRaw(::grpc::ClientContext* context) {
  return new ::grpc::ClientReaderWriter< ::Dealer::DealerRequest, ::Dealer::DealerRequest>(channel_.get(), rpcmethod_GameStream_, context);
}

::grpc::ClientAsyncReaderWriter< ::Dealer::DealerRequest, ::Dealer::DealerRequest>* Game::Stub::AsyncGameStreamRaw(::grpc::ClientContext* context, ::grpc::CompletionQueue* cq, void* tag) {
  return ::grpc::ClientAsyncReaderWriter< ::Dealer::DealerRequest, ::Dealer::DealerRequest>::Create(channel_.get(), cq, rpcmethod_GameStream_, context, tag);
}

Game::Service::Service() {
  AddMethod(new ::grpc::RpcServiceMethod(
      Game_method_names[0],
      ::grpc::RpcMethod::BIDI_STREAMING,
      new ::grpc::BidiStreamingHandler< Game::Service, ::Dealer::DealerRequest, ::Dealer::DealerRequest>(
          std::mem_fn(&Game::Service::GameStream), this)));
}

Game::Service::~Service() {
}

::grpc::Status Game::Service::GameStream(::grpc::ServerContext* context, ::grpc::ServerReaderWriter< ::Dealer::DealerRequest, ::Dealer::DealerRequest>* stream) {
  (void) context;
  (void) stream;
  return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
}


}  // namespace Dealer

