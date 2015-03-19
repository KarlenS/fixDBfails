import subprocess
import sys
import os
import argparse


def readlist(file):
  return {line[10:15]:line for line in file}


def lookforfails(runs,ofile):
  grepOut1 = subprocess.Popen(["grep","-rI","Database exception","logs/"], stdout=subprocess.PIPE)
  out1, err = grepOut1.communicate()
  
  grepOut2 = subprocess.Popen(["grep","-rI","Exception: Database: mysql_real_connect failed","logs/"], stdout=subprocess.PIPE)
  out2, err = grepOut2.communicate()
  
  for line in out1.split('\n'): 
    if len(line) > 1:
      run = line[5:10]

      runfile = run+".stage1.root"
      if os.path.exists(runfile):
        backupfails(runfile)
        ofile.write(runs[run]) #create a new runlist

  for line2 in out2.split('\n'): 
    if len(line2) > 1:
      run = line2[5:10]

      runfile = run+".stage1.root"
      
      if os.path.exists(runfile):
        backupfails(runfile)
        ofile.write(runs[run]) #create a new runlist

def backupfails(run):

  backupdir = "failed_runs"
  run_moved = backupdir+"/"+run

  if not os.path.exists(backupdir):
    "*** Creating new directory %s" %backupdir
    os.mkdir(backupdir)
  
  if os.path.exists(run):
    "*** Moving file %s" % run
    os.rename(run, run_moved) 

def resubmit_runs(runlist):
  grepOutNorm = subprocess.Popen(["vegas-stage1.pl","--analysis=.",runlist], stdout=subprocess.PIPE)
  out, err = grepOutNorm.communicate()
  print out


def main():

  parser = argparse.ArgumentParser(description='Fetches runs with DB-related issues and resubmits them.')
  parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="Runlist used for running stage1 (with .pl scripts).")
  args = parser.parse_args()
  
  failed_list = "runs_failed.list"
  outfile = open(failed_list,'w')

  runlist_dict = readlist(args.infile)
  lookforfails(runlist_dict,outfile)

  outfile.close()

  if (os.stat(failed_list).st_size > 0):
    resubmit_runs(failed_list)

if __name__ == '__main__':
  main()
