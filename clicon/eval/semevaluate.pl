#!/usr/bin/perl -w
# Parameters:
# -input (prediction directory)
# -gold (goldstandard directory)
# -n (specify name of run)
# -r (specify 1 or 2 for which run)
# -t (specifiy A, B)
# -a (optional - include if you used additional annotations)

# Output file: name + run + task + add/noadd (e.g. myrun.1.A.add)

# Example:
# perl eval.pl -n myrun -r 1 -t A -input Example -gold Gold -a

use strict;

use vars qw (%Pred %Gold @F $doc $bdary $tp $fp $fn $i @File $f);

use Getopt::Long;

my $add = "noadd";
my $name = "";
my $run = "";
my $input = "";
my $gold = "";
my $task = "";
my $error = "# Parameters:\n# -input (prediction file)\n# -gold (goldstandard file)\n# -n (specify name of run)\n# -r (specify 1 or 2 for which run)\n# -t (optional -- specifiy A, B), 2 for which task)\n# -a (optional - include if you used additional annotations)\n";


GetOptions ('a' => \$add,
      'n=s'=>\$name,
      'r=n'=>\$run,
      't=s'=>\$task,
      'input=s'=>\$input,
      'gold=s'=>\$gold    
    )||die "$error";

if (($name eq "")||($input eq "")||($gold eq "")) {
    die "$error";}
if (($run != 1)&&($run != 2)) {
    die "Incorrect run id\n";}
if (($task ne "A")&&($task ne "B")&&($task ne "2")) {
    die "Incorrect task id\n";}
if ($add eq "1") {
    $add = "add";
}

print $input;
# read predictions
opendir(D,$input)||die;
@File = grep /^[^\.].*[^\~]$/,readdir D;
closedir(D);
undef %Pred;
foreach $f (@File) {
    open(I,"$input/$f")||die "Input file not found: $input\/$f\n";

    while(<I>) {
  chomp;
  if ($_ !~ /^$/) {
      @F = split(/\|\|/,$_);      
      die "Error: incorrect number of arguments in prediction file: Line $.\n" if (not defined $F[4])||($#F % 2 != 0);
      foreach($i=3;$i<$#F;$i++) {die "Error: Span offsets should be in increasing order in the prediction file: Line $.\n" if $F[$i+1] < $F[$i];}
      $_ = join "\-",@F[3..$#F];
      $F[2] = lc($F[2]);
      $Pred{$F[0]}{$_} = $F[2];
  }
    }
    close(I);
}

# read goldstandard
opendir(D,$gold)||die;
@File = grep /^[^\.].*[^\~]$/,readdir D;
closedir(D);
undef %Gold;
foreach $f (@File) {
    open(I,"$gold/$f")||die "Goldstandard file not found: $gold\/$f\n";
    
    while(<I>) {
  chomp;
  if ($_ !~ /^$/) {
      @F = split(/\|\|/,$_);
      die "Error: incorrect number of arguments in goldstandard file: Line $.\n" if (not defined $F[4])||($#F % 2 != 0);
      foreach($i=3;$i<$#F;$i++) {die "Error: Span offsets should be in increasing order in the goldstandard file: Line $.\n" if $F[$i+1] < $F[$i];}
      $_ = join "\-",@F[3..$#F];
      $F[2] = lc($F[2]);
      $Gold{$F[0]}{$_} = $F[2]; 
  }
    }
    close(I);
}

open(O,">$name.$run.$task.$add")||die;

if ($task eq "A") {
    &taskA;
}
elsif ($task eq "B") {
    &taskB;
}
close(O);

sub taskA {

# TASK A

# strict
    $tp = 0; $fp = 0; $fn = 0;
    foreach $doc (keys %Pred) {
  foreach $bdary (keys %{$Pred{$doc}}) {
      if (defined $Gold{$doc}{$bdary}) {
    $tp++;
      }
      else {
    $fp++;
      }
  }
    }
    foreach $doc (keys %Gold) {
  foreach $bdary (keys %{$Gold{$doc}}) {
      if (not defined $Pred{$doc}{$bdary}) {
    $fn++;
      }
  }
    }
    
    print O "\n* Task A Strict:\n";
    &print_fsc($tp,$fp,$fn);
    
#relaxed
    $tp = 0; $fp = 0; $fn = 0;
    foreach $doc (keys %Pred) {
  foreach $bdary (keys %{$Pred{$doc}}) {
      if (&overlap($bdary,\%{$Gold{$doc}})) {
    $tp++;
      }
      else {
    $fp++;
      }
  }
    }
    foreach $doc (keys %Gold) {
  foreach $bdary (keys %{$Gold{$doc}}) {
      if (not &overlap($bdary,\%{$Pred{$doc}})) {
    $fn++;
      }
  }
    }

    print O "\n* Task A Relaxed:\n";
    &print_fsc($tp,$fp,$fn);
}

sub taskB {
# TASK B

# strict
    $tp = 0; $fp = 0; $fn = 0;
    foreach $doc (keys %Pred) {    
  foreach $bdary (keys %{$Pred{$doc}}) {  
      if ((defined $Gold{$doc}{$bdary})&&
    ($Gold{$doc}{$bdary} eq $Pred{$doc}{$bdary})) {     
    $tp++;
      }
  }
    }
    foreach $doc (keys %Gold) {
  foreach $bdary (keys %{$Gold{$doc}}) {
      if ((not defined $Pred{$doc}{$bdary})||
    ($Gold{$doc}{$bdary} ne $Pred{$doc}{$bdary})) {
    $fn++;
      }
  }
    }
    
    print O "\n* Task B Strict:\n";
    &print_acc($tp,$fp,$fn);
    
# relaxed
    
    $tp = 0; $fp = 0; $fn = 0;
    foreach $doc (keys %Pred) {    
  foreach $bdary (keys %{$Pred{$doc}}) {  
      if (defined $Gold{$doc}{$bdary}) {
    if ($Gold{$doc}{$bdary} eq $Pred{$doc}{$bdary}) {
        $tp++;
    }
    else {
        $fp++;
    }
      }
  }
    }
    
    print O "\n* Task B Relaxed:\n";
    &print_acc($tp,$fp,$fn);
}

sub print_fsc {
    my $tp = $_[0];
    my $fp = $_[1];
    my $fn = $_[2];

    my $p = 0; my $r = 0; my $f = 0;
    if ($tp != 0) { 
  $p = $tp / ($tp + $fp);
  $r = $tp / ($tp + $fn);
  $f = 2 * $p * $r / ($p + $r);
    }

    printf O ("Precision: \t%0.3f\n",$p);
    printf O ("Recall: \t%0.3f\n",$r);
    printf O ("F-score: \t%0.3f\n",$f);
}

sub print_acc {
    my $tp = $_[0];
    my $fp = $_[1];
    my $fn = $_[2];

    $_ = 0;
    if ($tp != 0) {
  $_ = $tp / ($tp + $fp + $fn);
    }

    printf O ("Accuracy: \t%0.3f\n",$_);
}

sub overlap {
    my $bdary = $_[0];
    my %Target = %{$_[1]};
    
    my (@F,$b1,$b2,$b_aux,@G,$i,%B1,%B2);
    my (@Pair1,@Pair2);
    my $out = 0;

    #obtain all subspans of target span
    @F = split(/\-/,$bdary);
    undef %B1;
    for($i=0;$i<=$#F;$i+=2) {
  $B1{"$F[$i]\-$F[$i+1]"} = 1;
    }
    #foreach subspan
    foreach $b1 (keys %B1) {
  @Pair1 = split(/\-/,$b1);
  #foreach span in target

  foreach $b_aux (keys %Target) {
      # obtain all subspans of the prediction
      @G = split(/\-/,$b_aux);
      undef %B2;
      for($i=0;$i<=$#G;$i+=2) {
    $B2{"$G[$i]\-$G[$i+1]"} = 1;
      }
      # foreach subspan
      foreach $b2 (keys %B2) {
    @Pair2 = split(/\-/,$b2);
    if (($Pair2[0] >= $Pair1[1])||($Pair1[0]>=$Pair2[1])) {
        next;
    }
    $out = 1;
    return $out;
      }
  }
    }
    return $out;
}
