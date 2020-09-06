"""Obtener info de la tabla de estadisticas en POX

Con este script, es posible obtener info de la tabla de estadisticas
El controlador consulta sobre el estado actual de la ruta de datos
utilizando el mensaje OFPT_STATS_REQEST.
----------------------------------------------------------------------
struct ofp_stats_request {  
    struct ofp_header header;
    uint16_t type; /* One of the OFPST_* constants. */
    uint16_t flags; /* OFPSF_REQ_* flags (none yet defined). */
    uint8_t body[0]; /* Body of the request. */
};
OFP_ASSERT(sizeof(struct ofp_stats_request) == 12);


class ofp_stats_request (ofp_header):
  def __init__ (self, **kw):
    ofp_header.__init__(self)
    self.header_type = OFPT_STATS_REQUEST
    self.type = None # Try to guess
    self.flags = 0
    self.body = b''

Donde:

  - type (int)      - el tipo de solicitud de estadisticas
  - flags (int)     - no hay banderas definidas en OpenFlow 1.0.
  - body (flexible) - cuerpo de la solicitud de estadisticas. 
                      Puede ser un objeto de bytes sin formato o 
                      una clase empaquetable (por ejemplo, ofp_port_stats_request).

(ver documentacion oficial de POX - seccion 5.3.5)
----------------------------------------------------------------------
Cuando el mensaje es enviado desde el controlador -> switch, este
responde con uno o varios mensajes de tipo OFPT_STATS_REPLY.
----------------------------------------------------------------------
struct ofp_stats_reply {  
    struct ofp_header header;
    uint16_t type; /* One of the OFPST_* constants. */
    uint16_t flags; /* OFPSF_REPLY_* flags. */
    uint8_t body[0]; /* Body of the reply. */
};
OFP_ASSERT(sizeof(struct ofp_stats_reply) == 12);
----------------------------------------------------------------------
Existe un campo "type" representa el tipo de info que se transmite.

En el script se monitorrea las entradas activas en los switches enviando
solicitudes de estadisticas de la tabla cuando se conectan controlador-swtich.
Cuando el controlador recibe el evento TableStateReceived, este maneja el evento 
y envia la slicitud de estadisticas por intervalos (default=10seg).

Ejecucion:
En ~/pox utilizar sudo ./pox.py log.level --DEBUG forwarding.l2_learning tableStat --interval=1

Obtenemos:
Un diccionario con las entradas activas de cada switch en la red.

"""

from pox.core import core  
from pox.lib.revent import *  
from pox.lib.recoco import Timer  
from collections import defaultdict  
from pox.lib.util import dpid_to_str  
from pox.openflow.discovery import Discovery 
import pox.openflow.libopenflow_01 as of  
import time

log = core.getLogger("WebStats")

class tableStats(EventMixin):  
  def __init__(self,interval = 10):
    self.tableActiveCount = {}
    self.interval = interval
    core.openflow.addListeners(self)

  def _handle_ConnectionUp(self,event):
    print "[!] Switch %s CONECTADO" %event.dpid
    self.sendTableStatsRequest(event)

  def _handle_TableStatsReceived(self,event):
    sw = 's%s'%event.dpid
    self.tableActiveCount[sw] = event.stats[0].active_count
    print "TableStatsReceived:"
    print self.tableActiveCount
    Timer(self.interval, self.sendTableStatsRequest,args=[event])

  def sendTableStatsRequest(self, event):
    sr = of.ofp_stats_request()
    sr.type = of.OFPST_TABLE
    event.connection.send(sr)
    print "[!] Enviando mensaje tableStat ------> Switch %s " %event.dpid

# When we get flow stats, print stuff out
def handle_flow_stats (event):
  web_bytes = 0
  web_flows = 0
  for f in event.stats:
    if f.match.tp_dst == 80 or f.match.tp_src == 80:
      web_bytes += f.byte_count
      web_flows += 1
  log.info("--------------Web traffic: %s bytes over %s flows", web_bytes, web_flows)


def launch(interval = '10'):  
  interval = int(interval)
  core.registerNew(tableStats,interval)

  # Listen for flow stats
  core.openflow.addListenerByName("FlowStatsReceived", handle_flow_stats)

  # Now actually request flow stats from all switches
  for con in core.openflow.connections: # make this _connections.keys() for pre-betta
    con.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
