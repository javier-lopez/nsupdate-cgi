# vi: set ft=ruby :
VAGRANTFILE_API_VERSION = '2'
Vagrant.require_version '>= 1.8.2'

CURRENT_DIR = File.expand_path(File.dirname(__FILE__))
DIRNAME     = File.basename(CURRENT_DIR)

hosts = [
    #10.10.10.1 is configured as bridged between the host and 10.10.1.x guests
    {
        :name  => "#{DIRNAME}.example.com",
        :box   => "minos/core-16.04",
        :ram   => "256", :cpus  => "1",
        :ip    => "10.10.10.11",
    },
]

host_os  = RbConfig::CONFIG['host_os']
if host_os =~ /linux/
    all_cpus = `nproc`.to_i
elsif host_os =~ /darwin/
    all_cpus = `sysctl -n hw.ncpu`.to_i
else #windows?
    all_cpus = `wmic cpu get NumberOfCores`.split("\n")[2].to_i
end

default_ram  = '512' #MB
default_cpu  = '50'  #%
default_cpus = all_cpus || '1'

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    hosts.each do |host|
        config.vm.define host[:name] do |machine|
            machine.vm.box      = host[:box]
            machine.vm.box_url  = host[:box_url] if host[:box_url]
            machine.vm.hostname = host[:name]

            machine.vm.network :private_network, ip: host[:ip]

            machine.vm.network "forwarded_port", guest: 80,   host: 8080, auto_correct: true, id:"httpd"

            machine.vm.synced_folder "html/",    "/var/www/html/",         create: true, id: "html"
            machine.vm.synced_folder "cgi-bin/", "/usr/lib/cgi-bin/",      create: true, id: "cgi-bin"
            machine.vm.synced_folder "scripts/", "/opt/nsupdate/scripts/", create: true, id: "scripts"

            machine.vm.provider "virtualbox" do |vbox|
                vbox.name = host[:name]
                vbox.linked_clone = true
                vbox.customize ["modifyvm", :id, "--memory", host[:ram] || default_ram ]          #MB
                vbox.customize ["modifyvm", :id, "--cpuexecutioncap", host[:cpu] || default_cpu ] #%
                vbox.customize ["modifyvm", :id, "--cpus", host[:cpus] || default_cpus ]
            end

            #echo cmds, lambda syntax: http://stackoverflow.com/questions/8476627/what-do-you-call-the-operator-in-ruby
            CMD_SCRIPT_ROOT        = -> (cmd) { machine.vm.provision 'shell', path:   cmd, name: cmd, privileged: true  }
            CMD_SCRIPT             = -> (cmd) { machine.vm.provision 'shell', path:   cmd, name: cmd, privileged: false }
            CMD_INLINE_ROOT        = -> (cmd) { machine.vm.provision 'shell', inline: cmd, name: cmd, privileged: true  }
            CMD_INLINE             = -> (cmd) { machine.vm.provision 'shell', inline: cmd, name: cmd, privileged: false }
            CMD_SCRIPT_ALWAYS_ROOT = -> (cmd) { machine.vm.provision 'shell', path:   cmd, name: cmd, run: "always", privileged: false }
            CMD_SCRIPT_ALWAYS      = -> (cmd) { machine.vm.provision 'shell', path:   cmd, name: cmd, run: "always", privileged: false }

            #authorize default public ssh key
            CMD_INLINE_ROOT.call("mkdir -p /root/.ssh/")
            CMD_INLINE.call     ("echo 'whoami?'; whoami")
            CMD_INLINE.call     ("mkdir -p ~/.ssh/")
            if File.file?("#{Dir.home}/.ssh/id_rsa.pub")
                ssh_pub_key = File.readlines("#{Dir.home}/.ssh/id_rsa.pub").first.strip
                CMD_INLINE_ROOT.call("printf '\\n%s\\n' '#{ssh_pub_key}' >> /root/.ssh/authorized_keys")
                CMD_INLINE.call     ("printf '\\n%s\\n' '#{ssh_pub_key}' >> ~/.ssh/authorized_keys")
            end

            #copy private ssh key
            if File.file?("#{Dir.home}/.ssh/id_rsa")
                machine.vm.provision "file",  source: "~/.ssh/id_rsa", destination: "~/.ssh/id_rsa"
                CMD_INLINE.call("chown $(whoami):$(whoami) ~/.ssh/id_rsa")
                CMD_INLINE.call("chmod 600 ~/.ssh/id_rsa")
            else
                if File.file?("ansible-local/ansible-local.pub")
                    ssh_pub_key = File.readlines("ansible-local/ansible-local.pub").first.strip
                    CMD_INLINE_ROOT.call("printf '\\n%s\\n' '#{ssh_pub_key}' >> /root/.ssh/authorized_keys")
                    CMD_INLINE.call     ("printf '\\n%s\\n' '#{ssh_pub_key}' >> ~/.ssh/authorized_keys")
                    machine.vm.provision "file",  source: "ansible-local/ansible-local.priv", destination: "~/.ssh/id_rsa"
                    CMD_INLINE.call     ("chown $(whoami):$(whoami) ~/.ssh/id_rsa")
                    CMD_INLINE.call     ("chmod 600 ~/.ssh/id_rsa")
                end
            end

            #copy gitconfig
            if File.file?("#{Dir.home}/.gitconfig")
                machine.vm.provision "file",  source: "~/.gitconfig", destination: "~/.gitconfig"
            end

            #provision
            Dir.glob("#{CURRENT_DIR}/provision/0*.sh").sort.each { |provision_script|
                CMD_SCRIPT.call(provision_script)
            }
        end
    end
end
