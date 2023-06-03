import argparse
import subprocess
import ctypes
import sys
import platform
import os
import psutil

def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin():
        # Already running with admin privileges
        return

    # Re-run the script with elevated permissions
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

def mount_image_windows(image_path):
    aim_cli_path = r'C:\\Users\\Ryan\\Downloads\\Arsenal-Image-Mounter-v3.9.239\\aim_cli.exe'
    command = [aim_cli_path, '--mount', '--readonly', f'--filename={image_path}', '--background']
    print(command)
    subprocess.run(command, shell=True)

    while True:
        print('-----Windows Mount Options Menu-----')
        print('1. Unmount Image and Exit')
        print('2. Display Current Volumes')
        print('3. Collect Targeted Files With KAPE')
        choice = input('Select an option:\n>')

        if choice == '1':
            command = [aim_cli_path, '--dismount', '--force']
            subprocess.run(command, shell=True)
            print("Now Exiting...")
            break
        elif choice == '2':
            print('Current Mounted Volumes: ')
            for part in psutil.disk_partitions():
                print(f'- Device: {part.device}')
                print(f' Mountpoint: {part.mountpoint}')
                print(f' File system type: {part.fstype}')
                print()
        elif choice =='3':
            #kape_path = input('Input the file path to KAPE cli: (Example: D:\Kape\)\n>')
            kape_path= r'c:\\users\\ryan\\downloads\\kape\\'
            print(kape_path)
            tsource = input('Select the soruce to collect from with KAPE: (Example: H:)\n>')
            tdest = input('Select where you like to save the KAPE collection: (D:\Kape)\n>')
            kape_command = [kape_path+'kape.exe', '--tsource',tsource,'--tdest',tdest,'--target', '!SANS_Triage']
            print(kape_command)
            subprocess.run(kape_command, shell=True)
        else:
            print('This is not the option you are looking for...')
       


    

def mount_image_linux(image_path, ewf_point, win_mount):
    if ewf_point is None:
        # Set a default mount point
        ewf_point = '/mnt/ewf_mount'
    else:
        pass
    print('Your EWF mount point is, ' + ewf_point)
    ewf_command = ['sudo', 'ewfmount', image_path, ewf_point]
    subprocess.run(ewf_command)
    ewf_path = ewf_point+'ewf1'

    #Use TSK's MMLS to identify starting byte offset and bytes per section
    mmls_command = ['sudo', 'mmls', ewf_path]
    subprocess.run(mmls_command)
    bytes_sector = input('What are the bytes per sector?\n>')
    bytes_sector = int(bytes_sector)
    starting_offset = input('What is the starting offset of the partition you would like to mount?\nLikely you want the largest length.\n>')
    starting_offset = int(starting_offset)
    calc_offset = bytes_sector*starting_offset
    calc_offset = str(calc_offset)
    #win_command = ['sudo','mount', '-t','ntfs-3g','-o','loop,ro,show_sys_files,stream_interface=windows,offset=$((',bytes_sector*starting_offset,'))',ewf_path, win_mount]
    #win_command = str(win_command)
    #subprocess.run(win_command)
    print('Attempting to mount identified file system....')
    os.system('''sudo mount -t ntfs-3g -o loop,ro,show_sys_files,stream_interface=windows,offset=$(('''+calc_offset+''')) '''+ewf_path+''' '''+win_mount)
    while True:
            print('-----Linux Mount Options Menu-----')
            print('1. Unmount Image and Exit')
            print('2. Display Current Volumes')
            choice = input('Select an option:\n> ')

            if choice == '1':
                print('Attempting to unmount the identified file system....')
                os.system('''sudo umount '''+win_mount)
                print('Attempting to unmount the EWF mount...')
                os.system('''sudo umount '''+ewf_point)
                print("Now Exiting...")
                break
            elif choice == '2':
                print('Current System Volumes: ')
                os.system('''df -h''')
            else:
                print('This is not the option you are looking for...')



if __name__ == '__main__':
    # Run the script with admin privileges on Windows
    print('Attempting to mount image....')
    if platform.system() == 'Windows':
        run_as_admin()
    else:
        pass

    parser = argparse.ArgumentParser(description='Mount an E01 forensic image using Arsenal Image Mounter.')
    parser.add_argument('-image', type=str, help='Path to the E01 image file')
    parser.add_argument('-ewf_mount', type=str, help='Linux path to mount point using ewftools(optional arguement, Linux only)')
    parser.add_argument('-win_mount', type=str, help='Linux path to mount point using ewftools(optional arguement, Linux only)')
    args = parser.parse_args()

    if args.image:
        image_path = args.image
        print('Your image is '+ image_path)

        if platform.system() == 'Windows':
            print("You are on a Windows host...")
            mount_image_windows(image_path)
        elif platform.system() == 'Linux':
            print("You are on a Linux host...")
            mount_image_linux(image_path, args.ewf_mount, args.win_mount)
        else:
            print("Unsupported operating system....")

