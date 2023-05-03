#!/usr/bin/env perl

use strict;
use warnings;
use feature qw(say);

use List::Util qw(max);
use Data::Dumper;

sub get_options {
   my %options;

   local $/;
   open my $fh, '<', '../src/ima/options.py' or die $!;

   $_ = <$fh>;
   {
      if ( m/\G
            .*?
            \s* parser\.add_option \s* \(
            \s* (?: '(?<o>-\w)'\s*, )? \s* (?: '(?<o> --\w+(?: (?>-\w+)+ )? )'\s*, )?
            \s* (?<args> (?: \s* \w+ \s* = \s* (?> (?: (?: '(?:[^']*|\\')?' | \d+ | False | True | None ) \s* )* ),? )* )
            \s* \) \s*
            /gsxo ) {

         my $option = join ' ', grep { defined } @{$-{o}};
         if ( my $args = $+{args} ) {

            if ( $args =~ m/ \s* metavar \s* = \s* '(?<v>.+?)' /x ) {
               $options{$option}{v} = $+{v};
            }

            my $description;
            if ( $args =~ m/ \s* help \s* = (?: \s* '(?<d>[^']*|\\'?)' (?{ $description .= $+{d} }) )+ /sx ) {
               $options{$option}{d} = $description;
            }
         }

         redo;
      }

   }

   print("End\n");
   return %options;
}

sub output_doc_options {
   my %options = @_;

   say '> Mandatory arguments to long options are mandatory for short options too.';
   foreach my $option ( keys %options ) {
      printf '> **%s**\n', $option;
      printf '>> %s\n', $options{$option};
   }
}

sub output_synopsis {
   my %options  = @_;
   my $synopsis = join ' ', map '[ ' . ( $_ =~ s/ /|/r ) . ( $options{$_}{v} // '' =~ s/(.+)/**$1**/r ) . ']', keys %options;

   say "# SYNOPSIS";
   printf "> **ima** %s **QUERY** [..QUERY]\n\n", $synopsis;
   say;
}

sub output_authors {
   open my $fh, '<', '../AUTHORS.md' or die $!;

   say "# AUTHORS";
   while ( <$fh> ) {
      printf "> %s\n", $1 if m/^\* (.+)$/;
   }
   say "";
}

sub output_file {
   my $file = shift;

   open my $fh, '<', $file or die $!;
   print while <$fh>;
   say "";
}

#output_file('./heading.md');

my %options = get_options();
say Dumper { %options };
#output_synopsis( %options );
#output_doc_options( %options );

#output_file('./body.md');
#output_authors();
#output_file('./issues.md');
#output_file('./license.md');
