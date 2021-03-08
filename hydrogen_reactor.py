# import scipy.constants
#
# mole = scipy.constants.physical_constants['Avogadro constant'][0]

mole = 6.02214076e23

""" 
    https://en.wikipedia.org/wiki/Proton%E2%80%93proton_chain_reaction 

    Mhc =  joules / kelvin * mol
    Mhc * kelvin / mol = joules
    
    Mhc =  joules / kelvin * mol
    mhc / mol = joules / kelvin
    mol / mhc = kelvin / joules
    mol / mhc * joules = kelvin 
    

    particles = grams / atm * mole
    Particles / mole = grams / atm
    Particles / mole * atm = grams

    specific heat of hydrogen = 
        Cv = 10.31 J/kg
"""

joule_to_mev = 6.242e12  # 1 joule = 6.242e12 MeV
mev_to_joule = 1.9226e-12 # 1 MeV = 1.9226e-12 joule


# joule = 6.242e12  # mega electron volts
# mev = 1.9226e-12 joule

def convert_grams_particles(grams, atomic_weight):
    return grams/atomic_weight*mole


def convert_particles_mole(particles, atomic_weight):
    return particles / mole * atomic_weight


class Element:
    protons = 0
    neutrons = 0
    electrons = 0
    stable = True
    half_life = None
    temperature = {'kelvins': 293}  # room temperature
    atomic_weight = 0  # grams per mole
    molar_heat_capacity = 0
    particles = 0  # quantity of the material in particles
    name = ''

    def __init__(self, name='', p=0, n=0, e=0, t=293, part=0):
        self.name = name
        self.protons = p
        self.neutrons = n
        self.elections = e
        self.temperature = t
        self.particles = part

    def add_particles(self, new_particles):
        self.particles += new_particles

    def add_grams(self, grams):
        self.particles += convert_grams_particles(grams, self.atomic_weight)

    def add_energy_joules(self, j):
        # Kelvin / mole = joules / mhc
        kelvin_increase_per_mole = j / self.molar_heat_capacity
        moles_of_material = self.particles / mole

        kelvin_increase = kelvin_increase_per_mole/moles_of_material

        self.temperature += kelvin_increase
        return

    def add(self, element):
        if not isinstance(element, Element):
            raise ValueError('type of argument must be Element')
        if element.name != self.name:
            raise ValueError('can only add element of the same kind')
        self.quantity += element.quantity


class Hydrogen(Element):
    def __init__(self, p=1, n=0, e=1, t=293, part=0):
        self.protons = p
        self.neutrons = n
        self.electrons = e
        self.temperature = t
        self.particles = part
        self.molar_heat_capacity = 28.836
        self.atomic_weight = 1.00784
        self.name = "Hydrogen-" + str(self.protons + self.neutrons)


class Helium(Element):
    def __init__(self, p=2, n=2, e=2, t=293, part=0):
        self.protons = p
        self.neutrons = n
        self.electrons = e
        self.temperature = t
        self.particles = part
        self.molar_heat_capacity = 20.78
        self.atomic_wight = 4.002602
        self.name = 'Helium-' + str(self.protons + self.neutrons)


class Reactor:
    #  p + p -> H(2,1) + positron + electron_nutrino 10 million kelvin
    #  positron + electron --> 1.442Mev
    #  H(2,1) + H(1,1) --> He(3,2) + 5.49Mev
    #  He(3,2) + He(3,2) --> He(4,2) + H(1,1) + H(1,1) + 12.86Mev
    in_tank = {}
    out_gamma = 0
    out_tank = {}
    reaction_time = {'second': 1}

    _deuterium_tank = 0
    _H1_tank = 0
    _He3_tank = 0
    _He4_tank = 0
    _neutrino_tank = 0
    _electron_tank = 0
    _positron_tank = 0
    _enegery_mev_tank = 0
    _proton_tank = 0
    _temperature = 293

    def __init__(self):
        pass

    def add(self, stuff: Element):
        # TODO: purge everyting in output tank (into surrounding area)
        have_already = self.in_tank.get(stuff.name)
        if have_already is None:
            self.in_tank[stuff.name] = stuff
            self._temperature = stuff.temperature
        else:
            have_already.add(stuff)

    def add_energy(self, energy_joules):
        count_materials = len(self.in_tank)
        for k in self.in_tank.keys():
            m = self.in_tank[k]
            m.add_energy_joules(energy_joules/count_materials)
        return

    def cycle(self):
        self.reaction_1()
        self.reaction_2()
        self.create_output()

    def reaction_1(self):
        # TODO: add a check for at least 10 million kelvin

        # 2 hydrogen in
        hydrogen = self.in_tank.get("Hydrogen-1")
        consumed = hydrogen.particles - (hydrogen.particles % 2)

        hydrogen.particles -= consumed
        # break out electrons on the atoms
        self._electron_tank += consumed

        #  p + p -> H(2,1) + positron + electron_neutrino
        produced = consumed / 2
        self._deuterium_tank += produced
        self._positron_tank += produced
        self._neutrino_tank += produced

        # positron, 2 electron, electron neutrino out
        particles_to_cancel = min(self._positron_tank, self._electron_tank)
        self._electron_tank -= particles_to_cancel
        self._positron_tank -= particles_to_cancel
        self._enegery_mev_tank += 1.442 * particles_to_cancel

    def reaction_2(self):
        # H(2,1) + H(1,1) --> He(3,2) + 5.49Mev
        consumed = self._deuterium_tank
        self._deuterium_tank -= consumed
        self._proton_tank -= consumed
        produced = consumed
        self._enegery_mev_tank += 5.49 * produced
        self._He3_tank += produced

    def reaction_3(self):
        #  He(3,2) + He(3,2) --> He(4,2) + H(1,1) + H(1,1) + 12.86Mev
        consumed = self._He3_tank - self._He3_tank % 2
        self._He3_tank -= consumed
        self._proton_tank += consumed
        produced = consumed / 2
        self._He4_tank += produced
        self._enegery_mev_tank += 12.86 * produced

    def create_output(self):
        self.out_gamma = self._enegery_mev_tank
        t = self._temperature
        if self._proton_tank > 0: self.out_tank['proton'] = Element('Hydrogen', 1, 0, 0, t, part=self._proton_tank)
        if self._positron_tank > 0: self.out_tank['positron'] = Element('Positron', 0, 0, 0, t, part=self._positron_tank)
        if self._electron_tank > 0: self.out_tank['electron'] = Element('Electron', 0, 0, 1, t, part=self._electron_tank)
        if self._neutrino_tank > 0: self.out_tank['neutrino'] = Element('Neutrino', 0, 0, 0, t, part=self._neutrino_tank)
        if self._He4_tank > 0: self.out_tank['Helium-4'] = Helium(p=2, n=2, e=0, t=t, part=self._He4_tank)
        if self._He3_tank > 0: self.out_tank['Helium-3'] = Helium(p=2, n=1, e=0, t=t, part=self._He3_tank)


if __name__ == "__main__":
    my_reactor = Reactor()
    material = Hydrogen()
    material.add_grams(100)
    my_reactor.add(material)
    my_reactor.add_energy(100000)
    my_reactor.cycle()
    output = my_reactor.out_tank
    power_out = my_reactor.out_gamma

    print(f'Energy produce = {power_out} MeV')
    print(f'reactants out = {output}')
    print('\n\n\nDone')
