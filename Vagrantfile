# vi: set ft=ruby :
VAGRANTFILE_API_VERSION = '2'
Vagrant.require_version '>= 1.8.2'

CURRENT_DIR = File.expand_path(File.dirname(__FILE__))
DIRNAME     = File.basename(CURRENT_DIR)

#host  = RbConfig::CONFIG['host_os']
hosts = {
    #10.10.10.1 is configured as bridged between the host and 10.10.1.x guests
    "#{DIRNAME}.example.com"  => "10.10.10.10",
}

#host_counter = 0; Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    hosts.each do |name, ip|
        config.vm.define name do |machine|
            machine.vm.box = "ubuntu/xenial64"
            machine.vm.hostname = name
            machine.vm.network :private_network, ip: ip

            machine.vm.network "forwarded_port", guest: 80,   host: 8080, auto_correct: true, id:"httpd"

            machine.vm.synced_folder "html/",    "/var/www/html/",         create: true, id: "html"
            machine.vm.synced_folder "cgi-bin/", "/usr/lib/cgi-bin/",      create: true, id: "cgi-bin"
            machine.vm.synced_folder "scripts/", "/opt/nsupdate/scripts/", create: true, id: "scripts"

            machine.vm.provider "virtualbox" do |vbox|
                vbox.name = name
                vbox.linked_clone = true if Vagrant::VERSION =~ /^1.8/
                if vbox.name.match(/^ubuntu/)
                    vbox.customize ["modifyvm", :id, "--memory", 1024]
                    vbox.customize ["modifyvm", :id, "--cpuexecutioncap", "80"]
                    #vbox.customize ["modifyvm", :id, "--cpuexecutioncap", "50"]
                #elsif vbox.name == "foo"
                    #vbox.customize ["modifyvm", :id, "--memory", 256]           #MB
                    #vbox.customize ["modifyvm", :id, "--cpuexecutioncap", "50"] #%
                else
                    vbox.customize ["modifyvm", :id, "--memory", 256]           #MB
                    vbox.customize ["modifyvm", :id, "--cpuexecutioncap", "50"] #%
                end
            end

            #$ vagrant plugin install vagrant-hosts
            if Vagrant.has_plugin?('vagrant-hosts')
                machine.vm.provision :hosts, sync_hosts: true
            elsif Vagrant.has_plugin?('vagrant-hostmanager')
                machine.hostmanager.enabled     = true
                machine.hostmanager.manage_host = true
                machine.hostmanager.aliases     = aliases
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
