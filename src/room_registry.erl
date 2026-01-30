-module(room_registry).
-behaviour(gen_server).

-export([
    start_link/0,
    join/3,
    leave/2,
    broadcast/3
]).

-export([
    init/1,
    handle_call/3,
    handle_cast/2
]).

-record(state, {rooms = #{}}).

start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

init([]) ->
    {ok, #state{}}.

join(Room, Pid, User) ->
    gen_server:call(?MODULE, {join, Room, Pid, User}).

leave(Room, Pid) ->
    gen_server:call(?MODULE, {leave, Room, Pid}).

broadcast(Room, From, Msg) ->
    gen_server:cast(?MODULE, {broadcast, Room, From, Msg}).

handle_call({join, Room, Pid, User}, _From, State) ->
    RoomMap = maps:get(Room, State#state.rooms, #{}),
    NewRoom = maps:put(Pid, User, RoomMap),
    NewRooms = maps:put(Room, NewRoom, State#state.rooms),
    {reply, ok, State#state{rooms = NewRooms}};

handle_call({leave, Room, Pid}, _From, State) ->
    RoomMap = maps:get(Room, State#state.rooms, #{}),
    NewRoom = maps:remove(Pid, RoomMap),
    NewRooms =
        case maps:size(NewRoom) of
            0 -> maps:remove(Room, State#state.rooms);
            _ -> maps:put(Room, NewRoom, State#state.rooms)
        end,
    {reply, ok, State#state{rooms = NewRooms}}.

handle_cast({broadcast, Room, From, Msg}, State) ->
    RoomMap = maps:get(Room, State#state.rooms, #{}),
    lists:foreach(
        fun({Pid, _}) ->
            if Pid =/= From -> Pid ! {send, Msg};
               true -> ok
            end
        end,
        maps:to_list(RoomMap)
    ),
    {noreply, State}.
