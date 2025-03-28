import os
import json
import signal
import xml.etree.ElementTree as ET
from datetime import datetime
from logger import get_logger

logger = get_logger("process_manager")

class ProcessManager:
    @staticmethod
    def get_process_info():       
        try:
            
            process_output = os.popen("ps aux").read()
            processes = []
                       
            lines = process_output.strip().split('\n')[1:]
            
            for line in lines:
               
                fields = line.split(None, 10)
                if len(fields) >= 11:
                    process = {
                        'user': fields[0],
                        'pid': fields[1],
                        'cpu': fields[2],
                        'mem': fields[3],
                        'vsz': fields[4],
                        'rss': fields[5],
                        'tty': fields[6],
                        'stat': fields[7],
                        'start': fields[8],
                        'time': fields[9],
                        'command': fields[10]
                    }
                    processes.append(process)
            
            return {'processes': processes, 'timestamp': datetime.now().isoformat()}
            
        except Exception as e:
            logger.error(f"Error getting process information: {str(e)}")
            raise

    def save_process_info(self, format="json"):
       
        try:
            process_info = self.get_process_info()
            filename = f"process_info.{format.lower()}"
            
            if format.lower() == "json":
                with open(filename, 'w') as f:
                    json.dump(process_info, f, indent=2)
            
            elif format.lower() == "xml":
                
                root = ET.Element("processes")
                timestamp = ET.SubElement(root, "timestamp")
                timestamp.text = process_info['timestamp']
                
                processes_elem = ET.SubElement(root, "process_list")
                for process in process_info['processes']:
                    proc_elem = ET.SubElement(processes_elem, "process")
                    for key, value in process.items():
                        elem = ET.SubElement(proc_elem, key)
                        elem.text = str(value)
                         
                tree = ET.ElementTree(root)
                tree.write(filename, encoding='utf-8', xml_declaration=True)
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Process information saved to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving process information: {str(e)}")
            raise

    def send_signal_to_process(self, pid, signal_name):
       
        try:
            
            sig = getattr(signal, signal_name)
            pid = int(pid)
            
          
            os.kill(pid, sig)
            message = f"Signal {signal_name} sent to process {pid} successfully"
            logger.info(message)
            return message
            
        except ValueError:
            message = f"Invalid process ID: {pid}"
            logger.error(message)
            raise ValueError(message)
        except AttributeError:
            message = f"Invalid signal name: {signal_name}"
            logger.error(message)
            raise ValueError(message)
        except ProcessLookupError:
            message = f"Process with ID {pid} not found"
            logger.error(message)
            raise ProcessLookupError(message)
        except PermissionError:
            message = f"Permission denied to send signal to process {pid}"
            logger.error(message)
            raise PermissionError(message)
        except Exception as e:
            message = f"Error sending signal to process: {str(e)}"
            logger.error(message)
            raise

if __name__ == "__main__":
   
    try:
        pm = ProcessManager()
       
        json_file = pm.save_process_info("json")
        logger.info(f"Test JSON file created: {json_file}")
        
       
        xml_file = pm.save_process_info("xml")
        logger.info(f"Test XML file created: {xml_file}")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
