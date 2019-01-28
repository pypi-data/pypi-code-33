from typing import Dict

from bzflag.networking.msg_add_player import MsgAddPlayerPacket
from bzflag.networking.msg_admin_info import MsgAdminInfoPacket
from bzflag.networking.msg_alive import MsgAlivePacket
from bzflag.networking.msg_capture_flag import MsgCaptureFlagPacket
from bzflag.networking.msg_drop_flag import MsgDropFlagPacket
from bzflag.networking.msg_flag_grab import MsgGrabFlagPacket
from bzflag.networking.msg_flag_update import MsgFlagUpdatePacket
from bzflag.networking.msg_game_time import MsgGameTimePacket
from bzflag.networking.msg_gm_update import MsgGMUpdatePacket
from bzflag.networking.msg_killed import MsgKilledPacket
from bzflag.networking.msg_message import MsgMessagePacket
from bzflag.networking.msg_new_rabbit import MsgNewRabbitPacket
from bzflag.networking.msg_null import MsgNullPacket
from bzflag.networking.msg_pause import MsgPausePacket
from bzflag.networking.msg_player_info import MsgPlayerInfoPacket
from bzflag.networking.msg_player_update import MsgPlayerUpdatePacket
from bzflag.networking.msg_remove_player import MsgRemovePlayerPacket
from bzflag.networking.msg_score import MsgScorePacket
from bzflag.networking.msg_score_over import MsgScoreOverPacket
from bzflag.networking.msg_set_var import MsgSetVarPacket
from bzflag.networking.msg_shot_begin import MsgShotBeginPacket
from bzflag.networking.msg_shot_end import MsgShotEndPacket
from bzflag.networking.msg_team_update import MsgTeamUpdatePacket
from bzflag.networking.msg_teleport import MsgTeleportPacket
from bzflag.networking.msg_time_update import MsgTimeUpdatePacket
from bzflag.networking.msg_transfer_flag import MsgTransferFlagPacket
from bzflag.networking.network_message import NetworkMessage


GamePacketMap: Dict[NetworkMessage, callable] = {
    NetworkMessage.Null: MsgNullPacket.factory,
    NetworkMessage.AddPlayer: MsgAddPlayerPacket.factory,
    NetworkMessage.AdminInfo: MsgAdminInfoPacket.factory,
    NetworkMessage.Alive: MsgAlivePacket.factory,
    NetworkMessage.CaptureFlag: MsgCaptureFlagPacket.factory,
    NetworkMessage.DropFlag: MsgDropFlagPacket.factory,
    NetworkMessage.GrabFlag: MsgGrabFlagPacket.factory,
    NetworkMessage.FlagUpdate: MsgFlagUpdatePacket.factory,
    NetworkMessage.GameTime: MsgGameTimePacket.factory,
    NetworkMessage.GMUpdate: MsgGMUpdatePacket.factory,
    NetworkMessage.Killed: MsgKilledPacket.factory,
    NetworkMessage.Message: MsgMessagePacket.factory,
    NetworkMessage.NewRabbit: MsgNewRabbitPacket.factory,
    NetworkMessage.Pause: MsgPausePacket.factory,
    NetworkMessage.PlayerInfo: MsgPlayerInfoPacket.factory,
    NetworkMessage.PlayerUpdate: MsgPlayerUpdatePacket.factory,
    NetworkMessage.PlayerUpdateSmall: MsgPlayerUpdatePacket.factory,
    NetworkMessage.RemovePlayer: MsgRemovePlayerPacket.factory,
    NetworkMessage.Score: MsgScorePacket.factory,
    NetworkMessage.ScoreOver: MsgScoreOverPacket.factory,
    NetworkMessage.SetVar: MsgSetVarPacket.factory,
    NetworkMessage.ShotBegin: MsgShotBeginPacket.factory,
    NetworkMessage.ShotEnd: MsgShotEndPacket.factory,
    NetworkMessage.TeamUpdate: MsgTeamUpdatePacket.factory,
    NetworkMessage.Teleport: MsgTeleportPacket.factory,
    NetworkMessage.TimeUpdate: MsgTimeUpdatePacket.factory,
    NetworkMessage.TransferFlag: MsgTransferFlagPacket.factory,
}
