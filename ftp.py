#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Libraries
from threading import Thread, Lock
from colorama import init
from time import sleep

import os, sys, paramiko

# Variables
SUCCESS = "[\x1b[32m+\x1b[39m]"
ERROR = "[\x1b[31m-\x1b[39m]"
INFO = "[\x1b[33m?\x1b[39m]"

# Includes
servers = [i.strip() for i in open("./data/servers.txt") if i]
lock = Lock()

# Server Information
password = "server password here" # Assuming all your server passwords are the same

class ExtendedSFTPClient(paramiko.SFTPClient):
    def putDir(self, localDir, serverDir):
        for file in os.listdir(localDir):
            if os.path.isfile(os.path.join(localDir, file)):
                self.put(os.path.join(localDir, file), "%s/%s" % (serverDir, file))
            else:
                self.mkdir("%s/%s" % (serverDir, file), ignoreExisting=True)
                self.putDir(os.path.join(localDir, file), "%s/%s" % (serverDir, file))

    def mkdir(self, path, mode=511, ignoreExisting=False):
        try:
            super(ExtendedSFTPClient, self).mkdir(path, mode)
        except IOError:
            if ignoreExisting:
                pass
            else:
                raise

class FTP(object):
	def __init__(self):
		super(FTP, self).__init__()

	def pushFiles(self, server, directory):
		try:
			with lock:
				stfpServer = paramiko.Transport((server, 22))
				stfpServer.connect(username="root", password=password)

				sftp = ExtendedSFTPClient.from_transport(stfpServer)
				sftp.mkdir("/root/" + directory, ignoreExisting=True)
				sftp.putDir("./files/" + directory, "/root/" + directory)

				print("%s Succcessfully uploaded %d files to %s..." % (SUCCESS, len(os.listdir("./files/" + directory)), server))

				sftp.close()
				stfpServer.close()
		except Exception as e:
			print(e)

class Threader(Thread):
	def __init__(self, ftp, server, directory):
		super(Threader, self).__init__()
		self.directory = directory
		self.server = server
		self.ftp = ftp

	def run(self):
		try:
			self.ftp.pushFiles(self.server, self.directory)
		except KeyboardInterrupt:
			return

def getInput(prompt):
	print(prompt, end="")

	try:
		return input().strip()
	except KeyboardInterrupt:
		print("\n", end="")
		exit(0)

def main():
	try:
		init()

		ftp = FTP()

		print("{} Removal's SFTP File Pusher | Version 1.0".format(INFO))
		print("\n{} Successfully loaded {:,} servers and {:,} directories ({})\n".format(SUCCESS, len(servers), len(os.listdir("./files")), ", ".join(os.listdir("./files"))))

		directory = getInput("{} Directory: ".format(INFO))

		print("\n%s Uploading %d files to %s...\n" % (INFO, len(os.listdir("./files/" + directory)), ", ".join(servers)))

		for i in range(len(servers)):
			thread = Threader(ftp, servers[i], directory)
			thread.setDaemon(True)
			thread.start()

		while True:
			sleep(0.15)
	except KeyboardInterrupt:
		print("\n%s FTP File Pusher stopped, exiting..." % ERROR)

if __name__ == "__main__":
	main()