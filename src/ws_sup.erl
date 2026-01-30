-module(ws_sup).
-behaviour(supervisor).

-export([start_link/0, init/1]).

start_link() ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, []).

init([]) ->
    Children = [
        {room_registry,
         {room_registry, start_link, []},
         permanent, 5000, worker, [room_registry]}
    ],
    {ok, {{one_for_one, 5, 10}, Children}}.
