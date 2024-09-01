import xml.etree.ElementTree as et
import logging
logger = logging.getLogger(__name__)


class XdlReader:
    def __init__(self):
        logging.basicConfig(filename='xdl_reader_log.txt', level=logging.INFO)
        logger.info('starting up')

    def load_xdl(self, xdl, is_file=True, clean_step=False):
        if is_file:
            try:
                tree = et.parse(xdl)
                tree = tree.getroot()
            except (FileNotFoundError, et.ParseError):
                logger.warning(f"{xdl} not found")
                return False
        else:
            try:
                tree = et.fromstring(xdl)
            except et.ParseError as e:
                logger.error(f"The XDL provided is not formatted correctly, {str(e)}")
                return False
        self.parse_xdl(tree, clean_step=clean_step)

    def parse_xdl(self, tree, clean_step=False):
        reagents = {}
        modules = {}
        if tree.find('Synthesis'):
            tree = tree.find('Synthesis')
        metadata = tree.find("Metadata")
        reaction_name = metadata.get('name')
        req_hardware = tree.find('Hardware')
        req_reagents = tree.find('Reagents')
        procedure = tree.find('Procedure')
        for reagent in req_reagents:
            reagent_name = reagent.get('id')
            # step for finding reagents in graph here
            # vessel = find_reagent(reagent_name)
            # reagents[reagent_name] = vessel
        for module in req_hardware:
            module_id = module.get('id')
            # searching setup for required hardware
            # modules[module_id] = find_target(module_id).name
        parse_success = True
        for step in procedure:
            if step.tag == "Add":
                if not self.process_xdl_add(modules, reagents, step):
                    parse_success = False
            elif step.tag == "Transfer":
                if not self.process_xdl_transfer(step):
                    parse_success = False
            elif 'Stir' in step.tag:
                if not self.process_xdl_stir(step):
                    parse_success = False
            elif "HeatChill" in step.tag:
                if not self.process_xdl_heatchill(step):
                    parse_success = False
            elif "Wait" in step.tag:
                if not self.process_xdl_wait(step, metadata):
                    parse_success = False
        if clean_step:
            response = input('press enter when done with cleaning')
        if not parse_success:
            raise Exception('XDL parsing was not successful')
        else:
            print('Reaction complete.')

    def process_xdl_add(self, modules, reagents, add_info):
        vessel = add_info.get('vessel')
        # TODO step for finding target in graph
        # target = find_target(vessel.lower())
        target = None
        if target is None:
            return False
        target = target.name
        source = reagents[add_info.get('reagent')]
        reagent_info = add_info.get('volume')
        if reagent_info is None:
            reagent_info = add_info.get('mass')
            # additional steps for solid reagents
            return
        else:
            reagent_info = reagent_info.split(' ')
            volume = float(reagent_info[0])
            if volume == 0:
                return True
            unit = reagent_info[1]
            if unit != 'ml':
                # assume uL
                # todo: update this to check a mapping
                volume = volume / 1000
        a_time = add_info.get('time')
        if a_time is not None:
            # flow should be in uL/min
            a_time = a_time.split(' ')
            if a_time[1] == 's':
                flow_rate = (volume * 1000) / (float(a_time[0]) / 60)
            else:
                flow_rate = (volume * 1000) / float(a_time[0])
        else:
            flow_rate = 0
        # TODO step for moving fluid from source to target
        # move_fluid(source, target, volume, flow_rate)
        return True

    def process_xdl_transfer(self, transfer_info):
        source = transfer_info.get('from_vessel')
        target = transfer_info.get('to_vessel')
        # TODO steps for finding target in graph
        # source = find_target(source).name
        # target = find_target(target).name
        if target is None or source is None:
            return False
        reagent_info = transfer_info.get('volume')
        if reagent_info is None:
            reagent_info = transfer_info.get('mass')
            return
        else:
            reagent_info = reagent_info.split(' ')
            volume = float(reagent_info[0])
            if volume == 0:
                return True
            unit = reagent_info[1]
            if unit != 'ml':
                volume = volume / 1000
        t_time = transfer_info.get('time')
        if t_time is not None:
            # uL/min
            t_time = t_time.split(' ')
            if t_time[1] == 's':
                flow_rate = (volume * 1000) / (float(t_time[0]) / 60)
            else:
                flow_rate = (volume * 1000) / float(t_time[0])
        else:
            flow_rate = 0
        # TODO step for moving fluid from source to target
        # move_fluid(source, target, volume, flow_rate, account_for_dead_volume=False, transfer=True)
        return True

    def process_xdl_stir(self, stir_info):
        reactor_name = stir_info.get('vessel')
        # TODO step for finding target
        # reactor = find_target(reactor_name.lower())
        reactor = None
        if reactor is None:
            return False
        reactor_name = reactor.name
        # StopStir
        if 'Stop' in stir_info.tag:
            # TODO step for stopping reactor stirring or heating
            # stop_reactor(reactor_name, command='stop_stir')
            return True
        else:
            speed = stir_info.get('stir_speed')
            speed = speed.split(' ')[0]
            stir_secs = stir_info.get('time')
            if stir_secs is None:
                stir_secs = 0
            else:
                stir_secs = stir_secs.split(' ')[0]
            # StartStir
            if 'Start' in stir_info.tag:
                # TODO step for starting stirring
                # start_stirring(reactor_name, command='start_stir', speed=float(speed), stir_secs=stir_secs, wait=False)
                pass
            # Stir
            else:
                # TODO step for starting stirring
                # self.manager.start_stirring(reactor_name, command='start_stir', speed=float(speed), stir_secs=int(stir_secs), wait=True)
            return True

    def process_xdl_heatchill(self, heatchill_info):
        reactor_name = heatchill_info.get('vessel')
        # TODO step for finding target device
        # reactor = find_target(reactor_name.lower())
        if reactor is None:
            return False
        reactor_name = reactor.name
        temp = heatchill_info.get('temp')
        heat_secs = heatchill_info.get('time')
        # StopHeatChill
        if 'Stop' in heatchill_info.tag:
            # TODO step for stopping reactor heating
            # stop_reactor(reactor_name, command='stop_heat')
            pass
        # StartHeatChill
        # Reactor will heat to specified temperature and stay on until end of reaction, or told to stop.
        elif 'Start' in heatchill_info.tag:
            temp = float(temp.split(' ')[0])
            # TODO step for starting heating
            # start_heating(reactor_name, command='start_heat', temp=temp, heat_secs=0, wait=False)
            pass
        # HeatChillToTemp
        # reactor will heat to required temperature and then turn off.
        elif 'To' in heatchill_info.tag:
            temp = float(temp.split(' ')[0])
            # TODO step for heating to target temperature
            # start_heating(reactor_name, command='start_heat', temp=temp, heat_secs=1, target=True, wait=True)
            pass
        # HeatChill
        # Reactor will heat to specified temperature for specified time.
        else:
            temp = float(temp.split(' ')[0])
            heat_secs = int(heat_secs.split(' ')[0])
            # TODO heating for certain time length
            # start_heating(reactor_name, command='start_heat', temp=temp, heat_secs=heat_secs, target=True, wait=True)
        return True

    def process_xdl_wait(self, wait_info, metadata):
        wait_time = wait_info.get('time')
        img_processing = metadata.get("img_processing")
        if wait_time is None:
            # TODO add wait step
            wait(wait_time=30, actions={})
        else:
            wait_time = wait_time.split(' ')
            unit = wait_time[1]
            if unit == 's' or unit == 'seconds':
                wait_time = int(wait_time[0])
            elif unit == 'min' or unit == 'minutes':
                wait_time = float(wait_time[0]) * 60
            # comments: "Picture<picture_no>, wait_user, wait_reason(reason)"
            comments = wait_info.get('comments')
            if comments is None:
                # todo add wait step
                wait(wait_time, {})
            else:
                add_actions = {}
                comments = comments.lower()
                comments = comments.split(',')
                for comment in comments:
                    if "picture" in comment:
                        pic_no = comment.split('picture')[1]
                        add_actions["picture"] = int(pic_no)
                        if img_processing is not None:
                            add_actions['img_processing'] = img_processing
                        else:
                            add_actions['img_processing'] = ''
                    elif "wait_user" in comment:
                        add_actions['wait_user'] = True
                    if "wait_reason" in comment:
                        reason = comment[comment.index('(') + 1:-1]
                        add_actions['wait_reason'] = reason
                # TODO add wait step
                wait(wait_time=wait_time, actions=add_actions)
        return True
